"""Custom exceptions for the accounts app."""


class OTPError(Exception):
    """Base class for OTP-related errors."""
    pass


class OTPExpiredError(OTPError):
    """Raised when the OTP has expired."""
    pass


class OTPMaxAttemptsError(OTPError):
    """Raised when the OTP has exceeded the maximum number of attempts."""
    pass


class OTPCooldownError(OTPError):
    """Raised when the OTP resend cooldown has not elapsed."""
    def __init__(self, remaining_seconds: int):
        self.remaining_seconds = remaining_seconds
        super().__init__(f"Please wait {remaining_seconds} seconds before requesting a new OTP.")


class OTPInvalidError(OTPError):
    """Raised when the submitted OTP does not match the stored hash."""
    pass


class OTPNotFoundError(OTPError):
    """Raised when no active OTP is found for the phone number."""
    pass
