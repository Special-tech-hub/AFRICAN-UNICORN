"""
Notification model: In-app notifications for drivers.
"""
import uuid
from django.db import models
from apps.accounts.models import User


class Notification(models.Model):
    """
    Stores in-app notifications for drivers.
    Structured for future email/SMS integration.
    """

    TYPE_OTP_SENT = 'OTP_SENT'
    TYPE_PHONE_VERIFIED = 'PHONE_VERIFIED'
    TYPE_APP_SUBMITTED = 'APP_SUBMITTED'
    TYPE_APP_UNDER_REVIEW = 'APP_UNDER_REVIEW'
    TYPE_APP_APPROVED = 'APP_APPROVED'
    TYPE_APP_REJECTED = 'APP_REJECTED'
    TYPE_NEW_APPLICATION = 'NEW_APPLICATION'  # For admin notifications
    NOTIFICATION_TYPE_CHOICES = [
        (TYPE_OTP_SENT, 'OTP Sent'),
        (TYPE_PHONE_VERIFIED, 'Phone Verified'),
        (TYPE_APP_SUBMITTED, 'Application Submitted'),
        (TYPE_APP_UNDER_REVIEW, 'Application Under Review'),
        (TYPE_APP_APPROVED, 'Application Approved'),
        (TYPE_APP_REJECTED, 'Application Rejected'),
        (TYPE_NEW_APPLICATION, 'New Application Submitted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', 'is_read'], name='notif_user_read_idx'),
            models.Index(fields=['user', 'created_at'], name='notif_user_time_idx'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.user.phone_number}"
