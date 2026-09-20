"""
File validators for document uploads.
Validates MIME type (from file bytes), extension, and file size.
"""
from pathlib import Path
from django.core.exceptions import ValidationError

ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'application/pdf']

MIME_TO_EXTENSIONS = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'application/pdf': ['.pdf'],
}


class MIMEValidator:
    """Validates file MIME type by inspecting file content bytes (not extension)."""

    def __call__(self, file):
        try:
            import magic
            file.seek(0)
            header = file.read(261)
            file.seek(0)
            mime = magic.from_buffer(header, mime=True)
        except ImportError:
            # Fallback if python-magic not installed: use extension-based guess
            import mimetypes
            file.seek(0)
            mime, _ = mimetypes.guess_type(getattr(file, 'name', ''))
            mime = mime or 'application/octet-stream'

        if mime not in ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"Unsupported file type '{mime}'. "
                f"Allowed types: JPEG, PNG, PDF."
            )
        return mime


class ExtensionValidator:
    """Validates that the file extension matches the detected MIME type."""

    def __call__(self, file, detected_mime: str):
        original_name = getattr(file, 'name', '')
        extension = Path(original_name).suffix.lower()
        allowed_extensions = MIME_TO_EXTENSIONS.get(detected_mime, [])
        if extension and extension not in allowed_extensions:
            raise ValidationError(
                f"File extension '{extension}' does not match the detected file type. "
                f"Expected one of: {', '.join(allowed_extensions)}"
            )


class FileSizeValidator:
    """Validates that the file size does not exceed 10 MB."""

    MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

    def __call__(self, file):
        if hasattr(file, 'size') and file.size > self.MAX_SIZE_BYTES:
            size_mb = file.size / (1024 * 1024)
            raise ValidationError(
                f"File size {size_mb:.1f} MB exceeds the maximum allowed size of 10 MB."
            )
