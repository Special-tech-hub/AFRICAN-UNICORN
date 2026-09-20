"""
Secure file storage utilities for uploaded documents.
Generates UUID-based filenames to prevent path traversal and enumeration.
"""
import uuid
from pathlib import Path


def document_upload_path(instance, filename: str) -> str:
    """
    Generate a safe storage path: documents/{user_id}/{uuid}.{ext}
    Files are stored outside any publicly accessible URL root.
    """
    extension = Path(filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{extension}"
    user_id = str(instance.driver.id) if hasattr(instance, 'driver') else 'unknown'
    return f"documents/{user_id}/{safe_name}"


def generate_safe_filename(original_filename: str) -> str:
    """Generate a UUID-based safe filename preserving the original extension."""
    extension = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4().hex}{extension}"
