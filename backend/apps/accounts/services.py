"""
OTP business logic service for TakeOFF Driver Onboarding Platform.
"""
import hashlib
import hmac
import logging
import os
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .exceptions import (
    OTPCooldownError,
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    OTPNotFoundError,
)
from .models import OTPVerification, User
from .otp_providers import get_otp_provider

logger = logging.getLogger(__name__)


class OTPService:
    """
    Handles all OTP generation, delivery, and verification logic.
    OTPs are hashed with PBKDF2-HMAC-SHA256 + per-record salt.
    Plaintext OTPs are never persisted.
    """

    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 60
    PBKDF2_ITERATIONS = 260_000

    @classmethod
    def _generate_otp(cls) -> str:
        """Generate a cryptographically secure 6-digit OTP, zero-padded."""
        return str(secrets.randbelow(10 ** cls.OTP_LENGTH)).zfill(cls.OTP_LENGTH)

    @classmethod
    def _hash_otp(cls, otp: str, salt: str) -> str:
        """Hash OTP using PBKDF2-HMAC-SHA256 with the given salt."""
        key = hashlib.pbkdf2_hmac(
            'sha256',
            otp.encode('utf-8'),
            salt.encode('utf-8'),
            cls.PBKDF2_ITERATIONS,
        )
        return key.hex()

    @classmethod
    def _verify_otp_hash(cls, submitted_otp: str, stored_hash: str, salt: str) -> bool:
        """Compare submitted OTP hash with stored hash using constant-time comparison."""
        computed = cls._hash_otp(submitted_otp, salt)
        return hmac.compare_digest(computed, stored_hash)

    @classmethod
    def generate_and_send(cls, user: User) -> None:
        """
        Generate a new OTP for the user, store it hashed, and send via configured provider.
        Enforces resend cooldown and invalidates any previous active OTPs.
        """
        with transaction.atomic():
            # Check resend cooldown
            latest_otp = (
                OTPVerification.objects
                .filter(user=user, is_active=True)
                .order_by('-created_at')
                .first()
            )
            if latest_otp:
                elapsed = (timezone.now() - latest_otp.created_at).total_seconds()
                remaining = cls.RESEND_COOLDOWN_SECONDS - elapsed
                if remaining > 0:
                    raise OTPCooldownError(int(remaining) + 1)

            # Invalidate previous active OTPs
            OTPVerification.objects.filter(user=user, is_active=True).update(is_active=False)

            # Generate OTP and hash it
            otp = cls._generate_otp()
            salt = secrets.token_hex(32)
            otp_hash = cls._hash_otp(otp, salt)

            # Store OTPVerification record
            OTPVerification.objects.create(
                user=user,
                otp_hash=otp_hash,
                otp_salt=salt,
                expires_at=timezone.now() + timedelta(minutes=cls.OTP_EXPIRY_MINUTES),
            )

        # Send OTP via configured provider (outside transaction)
        provider = get_otp_provider()
        provider.send(user.phone_number, otp)
        logger.info(f"OTP generated and sent for user {user.phone_number}")

        # Create notification (import here to avoid circular imports)
        try:
            from apps.notifications.services import NotificationService
            NotificationService.notify_otp_sent(user, user.phone_number)
        except Exception as e:
            logger.warning(f"Failed to create OTP notification: {e}")

    @classmethod
    def verify(cls, phone_number: str, submitted_otp: str) -> User:
        """
        Verify the submitted OTP for the given phone number.
        Returns the verified User on success.
        Raises typed exceptions on failure.
        """
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise OTPNotFoundError("No account found for this phone number.")

        with transaction.atomic():
            otp_record = (
                OTPVerification.objects
                .select_for_update()
                .filter(user=user, is_active=True)
                .order_by('-created_at')
                .first()
            )

            if otp_record is None:
                raise OTPNotFoundError("No active OTP found. Please request a new OTP.")

            # Check expiry before incrementing attempts
            if otp_record.is_expired:
                otp_record.is_active = False
                otp_record.save(update_fields=['is_active'])
                raise OTPExpiredError("OTP has expired. Please request a new one.")

            # Check attempt limit before incrementing
            if otp_record.attempt_count >= cls.MAX_ATTEMPTS:
                otp_record.is_active = False
                otp_record.save(update_fields=['is_active'])
                raise OTPMaxAttemptsError("Maximum OTP attempts exceeded. Please request a new OTP.")

            # Increment attempt count atomically
            otp_record.attempt_count += 1
            otp_record.save(update_fields=['attempt_count'])

            # Verify hash
            if not cls._verify_otp_hash(submitted_otp, otp_record.otp_hash, otp_record.otp_salt):
                # Check if this was the last allowed attempt
                if otp_record.attempt_count >= cls.MAX_ATTEMPTS:
                    otp_record.is_active = False
                    otp_record.save(update_fields=['is_active'])
                    raise OTPMaxAttemptsError("Maximum OTP attempts exceeded. Please request a new OTP.")
                raise OTPInvalidError("Invalid OTP. Please try again.")

            # Success — mark verified
            otp_record.is_active = False
            otp_record.verified_at = timezone.now()
            otp_record.save(update_fields=['is_active', 'verified_at'])

            # Mark user phone as verified
            user.is_phone_verified = True
            user.save(update_fields=['is_phone_verified'])

        logger.info(f"Phone verified successfully for {phone_number}")

        # Create notification
        try:
            from apps.notifications.services import NotificationService
            NotificationService.notify_phone_verified(user)
        except Exception as e:
            logger.warning(f"Failed to create phone verified notification: {e}")

        return user
