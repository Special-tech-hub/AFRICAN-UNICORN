"""
Pluggable OTP provider abstraction.
Set OTP_PROVIDER env var to switch between development (console) and production (SMS).
"""
import logging
from abc import ABC, abstractmethod
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseOTPProvider(ABC):
    """Abstract base class for OTP delivery providers."""

    @abstractmethod
    def send(self, phone_number: str, otp: str) -> None:
        """Send the OTP to the given phone number."""
        raise NotImplementedError


class ConsoleOTPProvider(BaseOTPProvider):
    """
    Development OTP provider.
    Logs OTP to console only — never used in production.
    """

    def send(self, phone_number: str, otp: str) -> None:
        logger.info(
            "=" * 60 + "\n"
            f"[DEV OTP] Phone: {phone_number}\n"
            f"[DEV OTP] OTP Code: {otp}\n"
            "=" * 60
        )


class TwilioOTPProvider(BaseOTPProvider):
    """
    Production SMS OTP provider via Twilio.
    Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER env vars.
    """

    def send(self, phone_number: str, otp: str) -> None:
        try:
            from twilio.rest import Client
        except ImportError:
            raise ImportError("twilio package is required for TwilioOTPProvider. Install it with: pip install twilio")

        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)

        if not all([account_sid, auth_token, from_number]):
            raise ValueError("Twilio credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER) are required.")

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=f"Your TakeOFF verification code is: {otp}. Valid for 10 minutes.",
            from_=from_number,
            to=phone_number,
        )
        logger.info(f"OTP SMS sent via Twilio to {phone_number[:4]}****")


def get_otp_provider() -> BaseOTPProvider:
    """
    Factory function that returns the configured OTP provider.
    Reads OTP_PROVIDER from Django settings (set via environment variable).
    """
    provider = getattr(settings, 'OTP_PROVIDER', 'console')

    if provider == 'console':
        return ConsoleOTPProvider()
    elif provider == 'twilio':
        return TwilioOTPProvider()
    else:
        raise ValueError(f"Unknown OTP provider: '{provider}'. Supported: 'console', 'twilio'.")
