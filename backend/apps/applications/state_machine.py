"""
Application state machine — enforces valid status transitions.
All transitions create an ApplicationStatusHistory record.
"""
import logging
from django.db import transaction
from django.utils import timezone
from .models import ApplicationStatusHistory

logger = logging.getLogger(__name__)

VALID_TRANSITIONS = {
    'DRAFT': ['SUBMITTED'],
    'SUBMITTED': ['UNDER_REVIEW'],
    'UNDER_REVIEW': ['APPROVED', 'REJECTED'],
    'APPROVED': [],
    'REJECTED': [],
}


class InvalidTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""
    pass


class ApplicationStateMachine:
    """
    Manages application status transitions.
    All transitions are atomic and recorded in history.
    """

    def transition(self, application, new_status: str, actor, note: str = '') -> None:
        current_status = application.status
        allowed = VALID_TRANSITIONS.get(current_status, [])

        if new_status not in allowed:
            raise InvalidTransitionError(
                f"Cannot transition from '{current_status}' to '{new_status}'. "
                f"Allowed: {allowed}"
            )

        with transaction.atomic():
            application.status = new_status
            if new_status == 'SUBMITTED':
                application.submitted_at = timezone.now()
            elif new_status in ('APPROVED', 'REJECTED'):
                application.reviewed_at = timezone.now()
                application.reviewed_by = actor
                if note:
                    application.review_note = note
            application.save()

            ApplicationStatusHistory.objects.create(
                application=application,
                previous_status=current_status,
                new_status=new_status,
                changed_by=actor,
                note=note,
            )

        logger.info(
            f"Application {application.id}: {current_status} → {new_status} "
            f"by {actor.phone_number}"
        )

        # Send notifications outside transaction
        self._send_notifications(application, new_status, note)

    def _send_notifications(self, application, new_status: str, note: str = '') -> None:
        try:
            from apps.notifications.services import NotificationService
            driver = application.driver
            ref = application.application_reference or str(application.id)

            if new_status == 'SUBMITTED':
                NotificationService.notify_app_submitted(driver, ref)
            elif new_status == 'UNDER_REVIEW':
                NotificationService.notify_app_under_review(driver, ref)
            elif new_status == 'APPROVED':
                NotificationService.notify_app_approved(driver, ref, note=note)
            elif new_status == 'REJECTED':
                NotificationService.notify_app_rejected(driver, ref, reason=note)
        except Exception as e:
            logger.warning(f"Notification failed for transition to {new_status}: {e}")


# Module-level singleton
state_machine = ApplicationStateMachine()
