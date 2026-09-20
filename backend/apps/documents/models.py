"""
Documents model: Stores uploaded document metadata.
"""
import uuid
from django.db import models
from apps.accounts.models import User


class Document(models.Model):
    """
    Stores metadata for a driver's uploaded document.
    The file field stores the path relative to MEDIA_ROOT.
    """

    TYPE_NATIONAL_ID = 'NATIONAL_ID'
    TYPE_DRIVERS_LICENSE = 'DRIVERS_LICENSE'
    TYPE_VEHICLE_REGISTRATION = 'VEHICLE_REGISTRATION'
    TYPE_INSURANCE = 'INSURANCE'
    TYPE_INSPECTION = 'INSPECTION'
    DOCUMENT_TYPE_CHOICES = [
        (TYPE_NATIONAL_ID, 'National ID / Passport'),
        (TYPE_DRIVERS_LICENSE, "Driver's Licence"),
        (TYPE_VEHICLE_REGISTRATION, 'Vehicle Registration'),
        (TYPE_INSURANCE, 'Insurance Certificate'),
        (TYPE_INSPECTION, 'Vehicle Inspection Certificate'),
    ]

    REQUIRED_DOCUMENT_TYPES = [
        TYPE_NATIONAL_ID,
        TYPE_DRIVERS_LICENSE,
        TYPE_VEHICLE_REGISTRATION,
        TYPE_INSURANCE,
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_VERIFIED = 'VERIFIED'
    STATUS_REJECTED = 'REJECTED'
    VERIFICATION_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_VERIFIED, 'Verified'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    application = models.ForeignKey(
        'applications.DriverApplication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='documents/')  # upload_to overridden in storage.py
    original_filename = models.CharField(max_length=255)
    safe_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    mime_type = models.CharField(max_length=100)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        indexes = [
            models.Index(fields=['driver', 'document_type'], name='doc_driver_type_idx'),
        ]
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.document_type} for {self.driver.phone_number}"
