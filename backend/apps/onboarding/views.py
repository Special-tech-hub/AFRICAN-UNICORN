"""Views for driver onboarding: profile, identity, vehicle."""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from core.permissions import IsDriverUser, IsPhoneVerified
from apps.applications.models import DriverApplication
from .models import DriverProfile, IdentityVerification, Vehicle
from .serializers import DriverProfileSerializer, IdentityVerificationSerializer, VehicleSerializer

logger = logging.getLogger(__name__)

ONBOARDING_PERMISSIONS = [IsAuthenticated, IsDriverUser, IsPhoneVerified]


@extend_schema(tags=['Driver Onboarding'])
class DriverProfileView(APIView):
    """GET/PUT driver personal and contact details."""
    permission_classes = ONBOARDING_PERMISSIONS

    def _ensure_draft_application(self, user):
        """Create a DRAFT application for the driver if one doesn't exist."""
        DriverApplication.objects.get_or_create(driver=user)

    @extend_schema(responses={200: DriverProfileSerializer})
    def get(self, request):
        profile, _ = DriverProfile.objects.get_or_create(user=request.user)
        return Response(DriverProfileSerializer(profile).data)

    @extend_schema(request=DriverProfileSerializer, responses={200: DriverProfileSerializer})
    def put(self, request):
        profile, _ = DriverProfile.objects.get_or_create(user=request.user)
        serializer = DriverProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self._ensure_draft_application(request.user)
        return Response(serializer.data)


@extend_schema(tags=['Driver Onboarding'])
class IdentityVerificationView(APIView):
    """GET/PUT identity and licence details."""
    permission_classes = ONBOARDING_PERMISSIONS

    @extend_schema(responses={200: IdentityVerificationSerializer})
    def get(self, request):
        identity, _ = IdentityVerification.objects.get_or_create(driver=request.user)
        return Response(IdentityVerificationSerializer(identity).data)

    @extend_schema(request=IdentityVerificationSerializer, responses={200: IdentityVerificationSerializer})
    def put(self, request):
        identity, _ = IdentityVerification.objects.get_or_create(driver=request.user)
        serializer = IdentityVerificationSerializer(identity, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(tags=['Driver Onboarding'])
class VehicleView(APIView):
    """GET/PUT vehicle details."""
    permission_classes = ONBOARDING_PERMISSIONS

    @extend_schema(responses={200: VehicleSerializer})
    def get(self, request):
        vehicle, _ = Vehicle.objects.select_related('driver').get_or_create(driver=request.user)
        return Response(VehicleSerializer(vehicle).data)

    @extend_schema(request=VehicleSerializer, responses={200: VehicleSerializer})
    def put(self, request):
        vehicle, _ = Vehicle.objects.select_related('driver').get_or_create(driver=request.user)
        serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
