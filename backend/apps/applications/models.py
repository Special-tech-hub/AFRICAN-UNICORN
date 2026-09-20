"""
Application models: DriverApplication, ApplicationStatusHistory, ApplicationSequence.
"""
import uuid
from django.db import models
from apps.accounts.models import User


class DriverApplication(models.Model):
    """
    Represents a driver's onboarding application.
    Follows a strict state machine: DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED | REJECTED.
    """

    STATUS_DRAFT = 'DRAFT'
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_UNDER_REVIEW = 'UNDER_REVIEW'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_reference = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text='Format: TO-YYYY-NNNNN. Assigned on submission.',
    )
    driver = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='application',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications',
    )
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'driver_application'
        verbose_name = 'Driver Application'
        verbose_name_plural = 'Driver Applications'
        indexes = [
            models.Index(fields=['status'], name='app_status_idx'),
            models.Index(fields=['application_reference'], name='app_reference_idx'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        ref = self.application_reference or 'DRAFT'
        return f"Application {ref} — {self.driver.phone_number} ({self.status})"


class ApplicationStatusHistory(models.Model):
    """Records every status transition for audit purposes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        DriverApplication,
        on_delete=models.CASCADE,
        related_name='status_history',
    )
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes',
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'application_status_history'
        verbose_name = 'Application Status History'
        verbose_name_plural = 'Application Status Histories'
        indexes = [
            models.Index(fields=['application', 'created_at'], name='status_hist_app_time_idx'),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.application.application_reference}: {self.previous_status} → {self.new_status}"


class ApplicationSequence(models.Model):
    """
    Tracks the per-year sequence counter for application reference generation.
    Uses SELECT FOR UPDATE for atomic increments under concurrent load.
    """

    year = models.IntegerField(unique=True)
    last_sequence = models.IntegerField(default=0)

    class Meta:
        db_table = 'application_sequence'
        verbose_name = 'Application Sequence'

    def __str__(self):
        return f"Sequence {self.year}: {self.last_sequence:05d}"
