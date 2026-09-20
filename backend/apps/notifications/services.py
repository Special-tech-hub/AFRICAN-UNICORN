"""Notification service for in-app notifications."""
import logging
from .models import Notification

logger = logging.getLogger(__name__)

NOTIFICATION_TEMPLATES = {
    'OTP_SENT': (
        'OTP Sent',
        'Your TakeOFF verification code has been sent to {phone}.',
    ),
    'PHONE_VERIFIED': (
        'Phone Verified',
        'Your phone number has been successfully verified. You can now start your onboarding.',
    ),
    'APP_SUBMITTED': (
        'Application Submitted',
        'Your driver application {ref} has been submitted and is awaiting review.',
    ),
    'APP_UNDER_REVIEW': (
        'Application Under Review',
        'Your driver application {ref} is now being reviewed by our team.',
    ),
    'APP_APPROVED': (
        'Application Approved \U0001f389',
        'Congratulations! Your driver application {ref} has been approved. {note}',
    ),
    'APP_REJECTED': (
        'Application Rejected',
        'Your driver application {ref} has been rejected. Reason: {reason}',
    ),
}


class NotificationService:
    """Creates in-app notification records for drivers."""

    @staticmethod
    def create(user, notification_type: str, title: str, message: str) -> Notification:
        try:
            return Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
            )
        except Exception as e:
            logger.error(f"Failed to create notification for {user.phone_number}: {e}")
            raise

    @classmethod
    def notify_otp_sent(cls, user, phone: str):
        title, msg = NOTIFICATION_TEMPLATES['OTP_SENT']
        cls.create(user, 'OTP_SENT', title, msg.format(phone=phone[:4] + '****'))

    @classmethod
    def notify_phone_verified(cls, user):
        title, message = NOTIFICATION_TEMPLATES['PHONE_VERIFIED']
        cls.create(user, 'PHONE_VERIFIED', title, message)

    @classmethod
    def notify_app_submitted(cls, user, reference: str):
        title, msg = NOTIFICATION_TEMPLATES['APP_SUBMITTED']
        cls.create(user, 'APP_SUBMITTED', title, msg.format(ref=reference))

    @classmethod
    def notify_app_under_review(cls, user, reference: str):
        title, msg = NOTIFICATION_TEMPLATES['APP_UNDER_REVIEW']
        cls.create(user, 'APP_UNDER_REVIEW', title, msg.format(ref=reference))

    @classmethod
    def notify_app_approved(cls, user, reference: str, note: str = ''):
        title, msg = NOTIFICATION_TEMPLATES['APP_APPROVED']
        note_text = f'Note: {note}' if note else ''
        cls.create(user, 'APP_APPROVED', title, msg.format(ref=reference, note=note_text))

    @classmethod
    def notify_app_rejected(cls, user, reference: str, reason: str):
        title, msg = NOTIFICATION_TEMPLATES['APP_REJECTED']
        cls.create(user, 'APP_REJECTED', title, msg.format(ref=reference, reason=reason))
