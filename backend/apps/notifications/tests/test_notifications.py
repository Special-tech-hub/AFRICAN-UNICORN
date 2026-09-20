"""Notification tests: creation, listing, mark-as-read, ownership."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def driver_a(db):
    return User.objects.create_user(
        phone_number='0771800001',
        password='Pass1234!',
        role='DRIVER',
        is_phone_verified=True,
    )


@pytest.fixture
def driver_b(db):
    return User.objects.create_user(
        phone_number='0771800002',
        password='Pass1234!',
        role='DRIVER',
        is_phone_verified=True,
    )


@pytest.mark.django_db
class TestNotificationService:
    def test_notify_otp_sent(self, driver_a):
        NotificationService.notify_otp_sent(driver_a, '0771800001')
        assert Notification.objects.filter(user=driver_a, notification_type='OTP_SENT').exists()

    def test_notify_phone_verified(self, driver_a):
        NotificationService.notify_phone_verified(driver_a)
        assert Notification.objects.filter(user=driver_a, notification_type='PHONE_VERIFIED').exists()

    def test_notify_app_submitted(self, driver_a):
        NotificationService.notify_app_submitted(driver_a, 'TO-2026-00001')
        assert Notification.objects.filter(user=driver_a, notification_type='APP_SUBMITTED').exists()

    def test_notify_app_approved(self, driver_a):
        NotificationService.notify_app_approved(driver_a, 'TO-2026-00001', note='Good job')
        assert Notification.objects.filter(user=driver_a, notification_type='APP_APPROVED').exists()

    def test_notify_app_rejected(self, driver_a):
        NotificationService.notify_app_rejected(driver_a, 'TO-2026-00001', reason='Licence expired')
        n = Notification.objects.filter(user=driver_a, notification_type='APP_REJECTED').first()
        assert n is not None
        assert 'Licence expired' in n.message


@pytest.mark.django_db
class TestNotificationAPI:
    def test_driver_sees_own_notifications(self, api_client, driver_a, driver_b):
        NotificationService.notify_phone_verified(driver_a)
        NotificationService.notify_phone_verified(driver_b)

        api_client.force_authenticate(user=driver_a)
        resp = api_client.get('/api/notifications/')
        assert resp.status_code == status.HTTP_200_OK
        for n in resp.data:
            # All returned notifications belong to driver_a
            assert n['notification_type'] is not None

        # Verify count — driver_a should only see their own
        count_a = Notification.objects.filter(user=driver_a).count()
        assert len(resp.data) == count_a

    def test_mark_notification_read(self, api_client, driver_a):
        n = NotificationService.notify_phone_verified(driver_a)
        assert n.is_read is False

        api_client.force_authenticate(user=driver_a)
        resp = api_client.patch(f'/api/notifications/{n.id}/read/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['is_read'] is True

    def test_driver_cannot_mark_others_notification(self, api_client, driver_a, driver_b):
        n = NotificationService.notify_phone_verified(driver_b)
        api_client.force_authenticate(user=driver_a)
        resp = api_client.patch(f'/api/notifications/{n.id}/read/')
        assert resp.status_code == status.HTTP_404_NOT_FOUND
