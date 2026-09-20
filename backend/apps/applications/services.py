"""
Application business logic: completeness validation and submission.
"""
import logging
from django.utils import timezone
from .models import DriverApplication
from .reference import generate_application_reference
from .state_machine import state_machine, InvalidTransitionError

logger = logging.getLogger(__name__)


class ApplicationService:
    """Service layer for driver application lifecycle."""

    REQUIRED_PROFILE_FIELDS = [
        'first_name', 'last_name', 'date_of_birth', 'gender', 'nationality',
        'email', 'street_address', 'city', 'province',
        'emergency_contact_name', 'emergency_contact_phone',
    ]
    REQUIRED_IDENTITY_FIELDS = [
        'id_type', 'id_number', 'drivers_license_number', 'license_expiry_date'
    ]
    REQUIRED_VEHICLE_FIELDS = [
        'vehicle_type', 'make', 'model', 'year', 'registration_number', 'colour'
    ]
    REQUIRED_DOCUMENT_TYPES = [
        'NATIONAL_ID', 'DRIVERS_LICENSE', 'VEHICLE_REGISTRATION', 'INSURANCE'
    ]

    @classmethod
    def validate_completeness(cls, driver) -> list:
        """
        Check all required fields and documents are present.
        Returns a list of missing item descriptions (empty = complete).
        """
        missing = []

        # DriverProfile
        try:
            profile = driver.driver_profile
            for field in cls.REQUIRED_PROFILE_FIELDS:
                if not getattr(profile, field, None):
                    label = field.replace('_', ' ').title()
                    missing.append(f"Profile: {label} is required.")
        except Exception:
            missing.append("Personal profile information is incomplete.")

        # IdentityVerification
        try:
            identity = driver.identity_verification
            for field in cls.REQUIRED_IDENTITY_FIELDS:
                if not getattr(identity, field, None):
                    label = field.replace('_', ' ').title()
                    missing.append(f"Identity: {label} is required.")
        except Exception:
            missing.append("Identity verification information is incomplete.")

        # Vehicle
        try:
            vehicle = driver.vehicle
            for field in cls.REQUIRED_VEHICLE_FIELDS:
                if not getattr(vehicle, field, None):
                    label = field.replace('_', ' ').title()
                    missing.append(f"Vehicle: {label} is required.")
        except Exception:
            missing.append("Vehicle information is incomplete.")

        # Required documents
        from apps.documents.models import Document
        uploaded_types = set(
            Document.objects.filter(driver=driver).values_list('document_type', flat=True)
        )
        doc_labels = dict(Document.DOCUMENT_TYPE_CHOICES)
        for doc_type in cls.REQUIRED_DOCUMENT_TYPES:
            if doc_type not in uploaded_types:
                missing.append(f"Document required: {doc_labels.get(doc_type, doc_type)}")

        return missing

    @classmethod
    def submit(cls, application: DriverApplication, driver) -> DriverApplication:
        """
        Validate completeness and submit the application (DRAFT → SUBMITTED).
        Raises InvalidTransitionError if not in DRAFT.
        Raises ValueError with list of missing items if incomplete.
        """
        if application.status != DriverApplication.STATUS_DRAFT:
            raise InvalidTransitionError("Application has already been submitted.")

        missing = cls.validate_completeness(driver)
        if missing:
            raise ValueError(missing)

        # Assign unique reference before transition
        reference = generate_application_reference()
        application.application_reference = reference
        application.save(update_fields=['application_reference'])

        # State transition (also sends notifications)
        state_machine.transition(application, 'SUBMITTED', actor=driver)

        logger.info(f"Application submitted: {reference} by {driver.phone_number}")
        return application
