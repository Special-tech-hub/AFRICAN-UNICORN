"""Views for driver application lifecycle."""
import logging
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from core.permissions import IsDriverUser, IsPhoneVerified
from .models import DriverApplication
from .serializers import DriverApplicationSerializer, ApplicationStatusSerializer
from .services import ApplicationService
from .state_machine import InvalidTransitionError

logger = logging.getLogger(__name__)


@extend_schema(tags=['Applications'])
class MyApplicationView(APIView):
    """Get the authenticated driver's current application."""
    permission_classes = [IsAuthenticated, IsDriverUser]

    @extend_schema(responses={200: DriverApplicationSerializer})
    def get(self, request):
        application = get_object_or_404(
            DriverApplication.objects.select_related('driver', 'reviewed_by'),
            driver=request.user,
        )
        return Response(DriverApplicationSerializer(application).data)


@extend_schema(tags=['Applications'])
class CreateApplicationView(APIView):
    """Create a DRAFT application for the driver (one per driver)."""
    permission_classes = [IsAuthenticated, IsDriverUser, IsPhoneVerified]

    @extend_schema(responses={201: DriverApplicationSerializer})
    def post(self, request):
        if DriverApplication.objects.filter(driver=request.user).exists():
            return Response(
                {'error': True, 'message': 'You already have an active application.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application = DriverApplication.objects.create(driver=request.user)
        return Response(
            DriverApplicationSerializer(application).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Applications'])
class SubmitApplicationView(APIView):
    """Submit the driver's DRAFT application after completeness validation."""
    permission_classes = [IsAuthenticated, IsDriverUser, IsPhoneVerified]

    @extend_schema(responses={200: DriverApplicationSerializer})
    def post(self, request, pk):
        application = get_object_or_404(DriverApplication, id=pk, driver=request.user)

        try:
            ApplicationService.submit(application, request.user)
        except InvalidTransitionError as e:
            return Response(
                {'error': True, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            missing = e.args[0] if e.args else []
            return Response(
                {'error': True, 'message': 'Application is incomplete.', 'missing': missing},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(DriverApplicationSerializer(application).data)


@extend_schema(tags=['Applications'])
class ApplicationStatusView(APIView):
    """Get the full status and history for a driver's application."""
    permission_classes = [IsAuthenticated, IsDriverUser]

    @extend_schema(responses={200: ApplicationStatusSerializer})
    def get(self, request, pk):
        application = get_object_or_404(
            DriverApplication.objects.prefetch_related('status_history__changed_by'),
            id=pk,
            driver=request.user,
        )
        return Response(ApplicationStatusSerializer(application).data)
