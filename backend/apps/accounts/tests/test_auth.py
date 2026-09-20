"""Authentication tests: registration, OTP, login, RBAC."""
import pytest
from datetime import timedelta
from django.core.management import call_command
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User, OTPVerification
from apps.accounts.services import OTPService


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def driver_user(db):
    user = User.objects.create_user(
        phone_number='0771000001',
        password='SecurePass123!',
        role='DRIVER',
    )
    return user


@pytest.fixture
def verified_driver(db):
    user = User.objects.create_user(
        phone_number='0771000002',
        password='SecurePass123!',
        role='DRIVER',
        is_phone_verified=True,
    )
    return user


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        phone_number='0700000001',
        password='AdminPass123!',
        role='ADMIN',
        is_phone_verified=True,
        is_staff=True,
    )
    return user


def make_otp(user, otp_value='123456', expired=False, max_attempts=False):
    import secrets
    salt = secrets.token_hex(32)
    otp_hash = OTPService._hash_otp(otp_value, salt)
    expires = (
        timezone.now() - timedelta(minutes=1)
        if expired
        else timezone.now() + timedelta(minutes=10)
    )
    return OTPVerification.objects.create(
        user=user,
        otp_hash=otp_hash,
        otp_salt=salt,
        expires_at=expires,
        attempt_count=5 if max_attempts else 0,
    )


@pytest.mark.django_db
class TestRegistration:
    def test_registration_success(self, api_client):
        resp = api_client.post('/api/auth/register/', {
            'phone_number': '0771111111',
            'password': 'StrongPass1!',
            'confirm_password': 'StrongPass1!',
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(phone_number='0771111111').exists()

    def test_duplicate_phone_returns_400(self, api_client, driver_user):
        resp = api_client.post('/api/auth/register/', {
            'phone_number': driver_user.phone_number,
            'password': 'StrongPass1!',
            'confirm_password': 'StrongPass1!',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_mismatch_returns_400(self, api_client):
        resp = api_client.post('/api/auth/register/', {
            'phone_number': '0771222222',
            'password': 'StrongPass1!',
            'confirm_password': 'Different1!',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_short_password_returns_400(self, api_client):
        resp = api_client.post('/api/auth/register/', {
            'phone_number': '0771333333',
            'password': '123',
            'confirm_password': '123',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_normalizes_phone_numbers_for_duplicates(self, api_client):
        first = api_client.post('/api/auth/register/', {
            'phone_number': '+263 771 111 111',
            'password': 'StrongPass1!',
            'confirm_password': 'StrongPass1!',
        })
        assert first.status_code == status.HTTP_201_CREATED

        second = api_client.post('/api/auth/register/', {
            'phone_number': '0771111111',
            'password': 'StrongPass1!',
            'confirm_password': 'StrongPass1!',
        })
        assert second.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestOTPVerification:
    def test_otp_verify_success(self, api_client, driver_user):
        otp_value = '654321'
        make_otp(driver_user, otp_value)
        resp = api_client.post('/api/auth/verify-otp/', {
            'phone_number': driver_user.phone_number,
            'otp': otp_value,
        })
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data
        driver_user.refresh_from_db()
        assert driver_user.is_phone_verified is True

    def test_expired_otp_returns_400(self, api_client, driver_user):
        make_otp(driver_user, expired=True)
        resp = api_client.post('/api/auth/verify-otp/', {
            'phone_number': driver_user.phone_number,
            'otp': '123456',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_otp_returns_400(self, api_client, driver_user):
        make_otp(driver_user, otp_value='999999')
        resp = api_client.post('/api/auth/verify-otp/', {
            'phone_number': driver_user.phone_number,
            'otp': '000000',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_max_attempts_returns_429(self, api_client, driver_user):
        make_otp(driver_user, max_attempts=True)
        resp = api_client.post('/api/auth/verify-otp/', {
            'phone_number': driver_user.phone_number,
            'otp': '123456',
        })
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, verified_driver):
        resp = api_client.post('/api/auth/login/', {
            'phone_number': verified_driver.phone_number,
            'password': 'SecurePass123!',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data

    def test_unverified_phone_returns_400(self, api_client, driver_user):
        resp = api_client.post('/api/auth/login/', {
            'phone_number': driver_user.phone_number,
            'password': 'SecurePass123!',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_wrong_password_returns_400(self, api_client, verified_driver):
        resp = api_client.post('/api/auth/login/', {
            'phone_number': verified_driver.phone_number,
            'password': 'WrongPass!',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_login_success(self, api_client, admin_user):
        resp = api_client.post('/api/auth/login/', {
            'phone_number': admin_user.phone_number,
            'password': 'AdminPass123!',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['user']['role'] == 'ADMIN'

    def test_login_accepts_equivalent_local_phone_format(self, api_client, verified_driver):
        user = User.objects.get(pk=verified_driver.pk)
        user.phone_number = '+263771000002'
        user.save(update_fields=['phone_number'])

        resp = api_client.post('/api/auth/login/', {
            'phone_number': '0771000002',
            'password': 'SecurePass123!',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data

    def test_seed_data_marks_existing_demo_accounts_as_verified(self, api_client):
        user = User.objects.create_user(
            phone_number='0771100001',
            password='Driver001!',
            role='DRIVER',
            is_phone_verified=False,
        )

        call_command('seed_data')
        user.refresh_from_db()

        assert user.is_phone_verified is True
        resp = api_client.post('/api/auth/login/', {
            'phone_number': '0771100001',
            'password': 'Driver001!',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data


@pytest.mark.django_db
class TestRBAC:
    def test_driver_cannot_access_admin_endpoint(self, api_client, verified_driver):
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.get('/api/admin/applications/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_profile(self, api_client):
        resp = api_client.get('/api/driver/profile/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
