"""Admin review tests: list, filter, approve, reject, statistics."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.applications.models import DriverApplication


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        phone_number='0700700001',
        password='Admin1234!',
        role='ADMIN',
        is_phone_verified=True,
        is_staff=True,
    )


@pytest.fixture
def driver_user(db):
    return User.objects.create_user(
        phone_number='0771700001',
        password='Pass1234!',
        role='DRIVER',
        is_phone_verified=True,
    )


@pytest.fixture
def submitted_application(db, driver_user, admin_user):
    app = DriverApplication.objects.create(
        driver=driver_user,
        status='SUBMITTED',
        application_reference='TO-2026-00001',
    )
    return app


@pytest.fixture
def under_review_application(db, driver_user, admin_user):
    app = DriverApplication.objects.create(
        driver=driver_user,
        status='UNDER_REVIEW',
        application_reference='TO-2026-00002',
    )
    return app


@pytest.mark.django_db
class TestAdminApplicationList:
    def test_admin_can_list_applications(self, api_client, admin_user, submitted_application):
        api_client.force_authenticate(user=admin_user)
        resp = api_client.get('/api/admin/applications/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_status_filter(self, api_client, admin_user, submitted_application):
        api_client.force_authenticate(user=admin_user)
        resp = api_client.get('/api/admin/applications/?status=SUBMITTED')
        assert resp.status_code == status.HTTP_200_OK
        for item in resp.data['results']:
            assert item['status'] == 'SUBMITTED'

    def test_driver_cannot_access_list(self, api_client, driver_user):
        api_client.force_authenticate(user=driver_user)
        resp = api_client.get('/api/admin/applications/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_list(self, api_client):
        resp = api_client.get('/api/admin/applications/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAdminApproveReject:
    def test_approve_success(self, api_client, admin_user, under_review_application):
        api_client.force_authenticate(user=admin_user)
        resp = api_client.post(
            f'/api/admin/applications/{under_review_application.id}/approve/',
            {'note': 'All good'},
        )
        assert resp.status_code == status.HTTP_200_OK
        under_review_application.refresh_from_db()
        assert under_review_application.status == 'APPROVED'

    def test_approve_non_under_review_returns_400(self, api_client, admin_user, submitted_application):
        api_client.force_authenticate(user=admin_user)
        resp = api_client.post(
            f'/api/admin/applications/{submitted_application.id}/approve/',
            {'note': 'Attempt'},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_reject_with_reason_success(self, api_client, admin_user, under_review_application):
        api_client.force_authenticate(user=admin_user)
        resp = api_client.post(
            f'/api/admin/applications/{under_review_application.id}/reject/',
            {'reason': 'Licence expired'},
        )
        assert resp.status_code == status.HTTP_200_OK
        under_review_application.refresh_from_db()
        assert under_review_application.status == 'REJECTED'
        assert under_review_application.review_note == 'Licence expired'

    def test_reject_without_reason_returns_400(self, api_client, admin_user, under_review_application):
        api_client.force_authenticate(user=admin_user)
        resp = api_client.post(
            f'/api/admin/applications/{under_review_application.id}/reject/',
            {'reason': ''},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_driver_cannot_approve(self, api_client, driver_user, under_review_application):
        api_client.force_authenticate(user=driver_user)
        resp = api_client.post(
            f'/api/admin/applications/{under_review_application.id}/approve/',
            {'note': 'Hack attempt'},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAdminStatistics:
    def test_statistics_returns_correct_counts(self, api_client, admin_user, db):
        # Create apps with different statuses
        for i, s in enumerate(['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED']):
            u = User.objects.create_user(
                phone_number=f'077190000{i}',
                password='Pass1234!',
                role='DRIVER',
                is_phone_verified=True,
            )
            DriverApplication.objects.create(driver=u, status=s)

        api_client.force_authenticate(user=admin_user)
        resp = api_client.get('/api/admin/statistics/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['DRAFT'] >= 1
        assert resp.data['SUBMITTED'] >= 1
        assert resp.data['APPROVED'] >= 1
        assert resp.data['REJECTED'] >= 1
        assert resp.data['total'] >= 5
