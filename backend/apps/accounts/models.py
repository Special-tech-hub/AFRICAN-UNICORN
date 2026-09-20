"""
Accounts models: Custom User and OTPVerification.
"""
import re
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


def normalize_phone_number(phone_number):
    """Normalize common Zimbabwean local/international phone formats to a canonical local number."""
    if phone_number is None:
        return ''

    value = re.sub(r'[\s\-()]', '', str(phone_number).strip())
    if not value:
        return ''

    if value.startswith('+'):
        value = value[1:]

    if value.startswith('00'):
        value = value[2:]

    if value.startswith('263'):
        value = '0' + value[3:]

    if not value.startswith('0'):
        value = '0' + value

    return value


def phone_number_variants(phone_number):
    """Return equivalent local/international forms for a phone number to support lookup and duplicates checks."""
    if phone_number is None:
        return []

    raw = re.sub(r'[\s\-()]', '', str(phone_number).strip())
    if not raw:
        return []

    variants = {raw}
    normalized = normalize_phone_number(raw)
    variants.add(normalized)

    if raw.startswith('+'):
        variants.add(raw[1:])
    if raw.startswith('00'):
        variants.add(raw[2:])
    if raw.startswith('263'):
        variants.add('0' + raw[3:])
    if raw.startswith('0'):
        variants.add('+263' + raw[1:])
        variants.add('263' + raw[1:])
    if raw.startswith('263') and len(raw) > 3:
        variants.add('0' + raw[3:])
    if raw and raw.isdigit() and not raw.startswith('0'):
        variants.add('0' + raw)

    return [v for v in variants if v]


class UserManager(BaseUserManager):
    """Custom manager for User model using phone_number as the unique identifier."""

    def get_by_natural_key(self, phone_number):
        for candidate in phone_number_variants(phone_number):
            try:
                return self.get(phone_number=candidate)
            except self.model.DoesNotExist:
                continue
        raise self.model.DoesNotExist(f"User matching phone number {phone_number} does not exist.")

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required.')

        phone_number = normalize_phone_number(phone_number)
        if not phone_number:
            raise ValueError('Phone number is required.')

        extra_fields.setdefault('role', 'DRIVER')
        extra_fields.setdefault('is_active', True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_phone_verified', True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model. Uses phone_number as the primary identifier.
    Supports DRIVER and ADMIN roles.
    """

    ROLE_DRIVER = 'DRIVER'
    ROLE_ADMIN = 'ADMIN'
    ROLE_CHOICES = [
        (ROLE_DRIVER, 'Driver'),
        (ROLE_ADMIN, 'Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_DRIVER)
    is_phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone_number} ({self.role})"

    @property
    def is_driver(self):
        return self.role == self.ROLE_DRIVER

    @property
    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN


class OTPVerification(models.Model):
    """
    Stores hashed OTP for phone number verification.
    Never stores plaintext OTP values.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otp_verifications',
    )
    otp_hash = models.CharField(max_length=256)
    otp_salt = models.CharField(max_length=64)  # Per-record salt for PBKDF2
    expires_at = models.DateTimeField()
    attempt_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'otp_verification'
        verbose_name = 'OTP Verification'
        verbose_name_plural = 'OTP Verifications'
        indexes = [
            models.Index(fields=['user', 'is_active'], name='otp_user_active_idx'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.phone_number} (active={self.is_active})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
