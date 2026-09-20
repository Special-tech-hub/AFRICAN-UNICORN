"""
Custom exception handler for TakeOFF Driver Onboarding Platform.
Returns consistent error response format.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wraps DRF errors in a consistent format:
    {"error": true, "message": "...", "details": {...}}
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': True,
            'message': _extract_message(response.data),
            'details': response.data,
        }
        response.data = error_data

    return response


def _extract_message(data):
    """Extract a human-readable message from DRF error data."""
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        for key, value in data.items():
            if isinstance(value, list) and value:
                return f"{key}: {value[0]}"
            if isinstance(value, str):
                return f"{key}: {value}"
    if isinstance(data, list) and data:
        return str(data[0])
    return 'An error occurred.'
