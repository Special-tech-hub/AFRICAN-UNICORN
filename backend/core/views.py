"""Core views: health check endpoint."""
import logging
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    GET /health/
    Returns operational status. Checks database connectivity.
    Returns 503 if DB is unavailable.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['System'],
        responses={
            200: {'type': 'object', 'properties': {'status': {'type': 'string'}}},
            503: {'type': 'object', 'properties': {'status': {'type': 'string'}, 'detail': {'type': 'string'}}},
        },
    )
    def get(self, request):
        try:
            connection.ensure_connection()
            return Response({'status': 'ok'})
        except OperationalError as e:
            logger.error(f"Health check DB failure: {e}")
            return Response(
                {'status': 'degraded', 'detail': 'database unavailable'},
                status=503,
            )
