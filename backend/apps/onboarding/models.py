"""
Onboarding models: DriverProfile, IdentityVerification, Vehicle.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class DriverProfile(models.Model):
    """Stores personal and contact details for a driver."""

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
        ('PREFER_NOT_TO_SAY', 'Prefer not to say'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile',
    )
    # Personal details
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    # Contact details
    email = models.EmailField(max_length=254, blank=True)
    street_address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'driver_profile'
        verbose_name = 'Driver Profile'
        verbose_name_plural = 'Driver Profiles'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.phone_number})"

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(p for p in parts if p).strip()

    def is_personal_complete(self):
        """Check if all required personal detail fields are filled."""
        return all([
            self.first_name,
            self.last_name,
            self.date_of_birth,
            self.gender,
            self.nationality,
        ])

    def is_contact_complete(self):
        """Check if all required contact detail fields are filled."""
        return all([
            self.email,
            self.street_address,
            self.city,
            self.province,
            self.emergency_contact_name,
            self.emergency_contact_phone,
        ])


class IdentityVerification(models.Model):
    """Stores identity and driving licence information for a driver."""

    ID_TYPE_NATIONAL = 'NATIONAL_ID'
    ID_TYPE_PASSPORT = 'PASSPORT'
    ID_TYPE_CHOICES = [
        (ID_TYPE_NATIONAL, 'National ID'),
        (ID_TYPE_PASSPORT, 'Passport'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='identity_verification',
    )
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES, blank=True)
    id_number = models.CharField(max_length=100, blank=True)
    drivers_license_number = models.CharField(max_length=100, blank=True)
    license_expiry_date = models.DateField(null=True, blank=True)
    is_license_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'identity_verification'
        verbose_name = 'Identity Verification'
        verbose_name_plural = 'Identity Verifications'

    def __str__(self):
        return f"Identity: {self.driver.phone_number} ({self.id_type})"

    def save(self, *args, **kwargs):
        # Auto-set is_license_expired based on expiry date
        if self.license_expiry_date:
            self.is_license_expired = self.license_expiry_date < timezone.now().date()
        super().save(*args, **kwargs)

    def is_complete(self):
        return all([
            self.id_type,
            self.id_number,
            self.drivers_license_number,
            self.license_expiry_date,
        ])


class Vehicle(models.Model):
    """Stores vehicle details for a driver."""

    TYPE_MOTORCYCLE = 'MOTORCYCLE'
    TYPE_SEDAN = 'SEDAN'
    TYPE_HATCHBACK = 'HATCHBACK'
    TYPE_PICKUP = 'PICKUP'
    TYPE_VAN = 'VAN'
    TYPE_TRUCK = 'TRUCK'
    TYPE_CHOICES = [
        (TYPE_MOTORCYCLE, 'Motorcycle'),
        (TYPE_SEDAN, 'Sedan'),
        (TYPE_HATCHBACK, 'Hatchback'),
        (TYPE_PICKUP, 'Pickup'),
        (TYPE_VAN, 'Van'),
        (TYPE_TRUCK, 'Truck'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vehicle',
    )
    vehicle_type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True)
    make = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(null=True, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    colour = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicle'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.registration_number})"

    def is_complete(self):
        return all([
            self.vehicle_type,
            self.make,
            self.model,
            self.year,
            self.registration_number,
            self.colour,
        ])
