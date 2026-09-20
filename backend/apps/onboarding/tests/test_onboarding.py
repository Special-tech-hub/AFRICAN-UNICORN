"""Onboarding tests: profile, identity, vehicle."""
import pytest
from datetime import date
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_driver(db):
    return User.objects.create_user(
        phone_number='0771500001',
        password='Pass1234!',
        role='DRIVER',
        is_phone_verified=True,
    )


@pytest.fixture
def verified_driver_2(db):
    return User.objects.create_user(
        phone_number='0771500002',
        password='Pass1234!',
        role='DRIVER',
        is_phone_verified=True,
    )


@pytest.mark.django_db
class TestDriverProfile:
    def test_profile_create(self, api_client, verified_driver):
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.put('/api/driver/profile/', {
            'first_name': 'Tendai',
            'last_name': 'Moyo',
            'date_of_birth': '1990-03-15',
            'gender': 'MALE',
            'nationality': 'Zimbabwean',
            'email': 'tendai@example.com',
            'street_address': '12 Main St',
            'city': 'Harare',
            'province': 'Harare',
            'emergency_contact_name': 'Grace',
            'emergency_contact_phone': '0771200001',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['first_name'] == 'Tendai'

    def test_profile_get(self, api_client, verified_driver):
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.get('/api/driver/profile/')
        assert resp.status_code == status.HTTP_200_OK

    def test_unauthenticated_returns_401(self, api_client):
        resp = api_client.get('/api/driver/profile/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestIdentityVerification:
    def test_identity_create_with_expired_licence(self, api_client, verified_driver):
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.put('/api/driver/identity/', {
            'id_type': 'NATIONAL_ID',
            'id_number': 'TEST-001',
            'drivers_license_number': 'DL-TEST-001',
            'license_expiry_date': '2020-01-01',  # Expired
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['is_license_expired'] is True

    def test_identity_create_valid(self, api_client, verified_driver):
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.put('/api/driver/identity/', {
            'id_type': 'PASSPORT',
            'id_number': 'PASS-TEST-001',
            'drivers_license_number': 'DL-TEST-002',
            'license_expiry_date': '2030-12-31',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['is_license_expired'] is False


@pytest.mark.django_db
class TestVehicle:
    def test_vehicle_create_success(self, api_client, verified_driver):
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.put('/api/driver/vehicle/', {
            'vehicle_type': 'SEDAN',
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'registration_number': 'ABC123',
            'colour': 'White',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['make'] == 'Toyota'

    def test_vehicle_year_too_early_returns_400(self, api_client, verified_driver):
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.put('/api/driver/vehicle/', {
            'vehicle_type': 'SEDAN',
            'make': 'Old',
            'model': 'Car',
            'year': 1800,
            'registration_number': 'OLD001',
            'colour': 'Brown',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
