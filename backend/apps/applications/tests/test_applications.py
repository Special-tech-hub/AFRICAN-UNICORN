"""Application tests: DRAFT creation, submission, state machine."""
import pytest
from datetime import date
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.applications.models import DriverApplication, ApplicationSequence
from apps.applications.reference import generate_application_reference
from apps.applications.state_machine import state_machine, InvalidTransitionError
from apps.onboarding.models import DriverProfile, IdentityVerification, Vehicle
from apps.documents.models import Document
from django.core.files.base import ContentFile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_driver(db):
    return User.objects.create_user(
        phone_number='0771600001',
        password='Pass1234!',
        role='DRIVER',
        is_phone_verified=True,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        phone_number='0700600001',
        password='Admin1234!',
        role='ADMIN',
        is_phone_verified=True,
        is_staff=True,
    )


def create_full_application(driver):
    """Helper: create all required data for a complete application."""
    DriverProfile.objects.update_or_create(driver=driver, user=driver, defaults={
        'first_name': 'Test', 'last_name': 'Driver',
        'date_of_birth': date(1990, 1, 1), 'gender': 'MALE',
        'nationality': 'Zimbabwean', 'email': 'test@example.com',
        'street_address': '1 Test St', 'city': 'Harare',
        'province': 'Harare', 'emergency_contact_name': 'Jane',
        'emergency_contact_phone': '0771000000',
    })
    IdentityVerification.objects.update_or_create(driver=driver, defaults={
        'id_type': 'NATIONAL_ID', 'id_number': 'NID-TEST',
        'drivers_license_number': 'DL-TEST', 'license_expiry_date': date(2030, 1, 1),
    })
    Vehicle.objects.update_or_create(driver=driver, defaults={
        'vehicle_type': 'SEDAN', 'make': 'Toyota', 'model': 'Corolla',
        'year': 2020, 'registration_number': 'TST001', 'colour': 'White',
    })
    app, _ = DriverApplication.objects.get_or_create(driver=driver)
    for doc_type in ['NATIONAL_ID', 'DRIVERS_LICENSE', 'VEHICLE_REGISTRATION', 'INSURANCE']:
        if not Document.objects.filter(driver=driver, document_type=doc_type).exists():
            doc = Document(
                driver=driver, application=app, document_type=doc_type,
                original_filename=f'{doc_type}.pdf', safe_filename=f'{doc_type}_safe.pdf',
                file_size=100, mime_type='application/pdf',
            )
            doc.file.save(f'{doc_type}.pdf', ContentFile(b'%PDF fake'), save=True)
    return app


@pytest.mark.django_db
class TestApplicationCreation:
    def test_draft_creation_success(self, api_client, verified_driver):
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.post('/api/applications/')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['status'] == 'DRAFT'

    def test_duplicate_draft_returns_400(self, api_client, verified_driver):
        DriverApplication.objects.create(driver=verified_driver)
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.post('/api/applications/')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestApplicationSubmission:
    def test_full_submission_success(self, api_client, verified_driver):
        app = create_full_application(verified_driver)
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.post(f'/api/applications/{app.id}/submit/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['status'] == 'SUBMITTED'
        assert resp.data['application_reference'].startswith('TO-')

    def test_submit_already_submitted_returns_400(self, api_client, verified_driver):
        app = create_full_application(verified_driver)
        app.status = 'SUBMITTED'
        app.application_reference = 'TO-2026-99999'
        app.save()
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.post(f'/api/applications/{app.id}/submit/')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_missing_docs_returns_400(self, api_client, verified_driver):
        DriverApplication.objects.get_or_create(driver=verified_driver)
        app = DriverApplication.objects.get(driver=verified_driver)
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.post(f'/api/applications/{app.id}/submit/')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert 'missing' in resp.data


@pytest.mark.django_db
class TestStateMachine:
    def test_invalid_transition_raises_error(self, verified_driver):
        app = DriverApplication.objects.create(driver=verified_driver)
        with pytest.raises(InvalidTransitionError):
            state_machine.transition(app, 'APPROVED', actor=verified_driver)

    def test_valid_transition_creates_history(self, verified_driver):
        app = create_full_application(verified_driver)
        from apps.applications.services import ApplicationService
        ApplicationService.submit(app, verified_driver)
        app.refresh_from_db()
        assert app.status == 'SUBMITTED'
        assert app.status_history.count() >= 1


@pytest.mark.django_db
class TestReferenceGeneration:
    def test_references_are_unique(self, db):
        ref1 = generate_application_reference()
        ref2 = generate_application_reference()
        assert ref1 != ref2
        assert ref1.startswith('TO-')
        assert ref2.startswith('TO-')

    def test_reference_format(self, db):
        import re
        ref = generate_application_reference()
        assert re.match(r'^TO-\d{4}-\d{5}$', ref)
