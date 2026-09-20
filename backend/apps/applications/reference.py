"""
Atomic application reference number generator.
Uses SELECT FOR UPDATE to guarantee uniqueness under concurrent requests.
"""
from django.db import transaction
from django.utils import timezone
from .models import ApplicationSequence


def generate_application_reference() -> str:
    """
    Generate a unique reference in the format TO-YYYY-NNNNN.
    Uses a DB-level lock to prevent duplicates under concurrency.
    """
    year = timezone.now().year
    with transaction.atomic():
        seq_obj, _ = ApplicationSequence.objects.select_for_update().get_or_create(
            year=year,
            defaults={'last_sequence': 0},
        )
        seq_obj.last_sequence += 1
        seq_obj.save(update_fields=['last_sequence'])
        return f"TO-{year}-{seq_obj.last_sequence:05d}"
