"""Admin review views: list, detail, approve, reject, statistics."""
import logging
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from core.permissions import IsAdminUser
from core.pagination import StandardPagination
from apps.applications.models import DriverApplication
from apps.applications.state_machine import state_machine, InvalidTransitionError
from .serializers import (
    AdminApplicationListSerializer,
    AdminApplicationDetailSerializer,
    ApproveSerializer,
    RejectSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=['Admin'])
class AdminApplicationListView(APIView):
    """List all applications with optional status filter and search."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(responses={200: AdminApplicationListSerializer(many=True)})
    def get(self, request):
        queryset = (
            DriverApplication.objects
            .select_related('driver', 'driver__driver_profile', 'driver__vehicle', 'reviewed_by')
            .order_by('-created_at')
        )

        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        # Search by name, phone, or reference
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(application_reference__icontains=search) |
                Q(driver__phone_number__icontains=search) |
                Q(driver__driver_profile__first_name__icontains=search) |
                Q(driver__driver_profile__last_name__icontains=search)
            )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AdminApplicationListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


@extend_schema(tags=['Admin'])
class AdminApplicationDetailView(APIView):
    """Get full application details. Auto-transitions SUBMITTED → UNDER_REVIEW."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(responses={200: AdminApplicationDetailSerializer})
    def get(self, request, pk):
        application = get_object_or_404(
            DriverApplication.objects
            .select_related('driver', 'reviewed_by')
            .prefetch_related('status_history__changed_by', 'driver__driver_profile',
                              'driver__identity_verification', 'driver__vehicle'),
            id=pk,
        )

        # Auto-transition SUBMITTED → UNDER_REVIEW when admin opens it
        if application.status == DriverApplication.STATUS_SUBMITTED:
            try:
                state_machine.transition(application, 'UNDER_REVIEW', actor=request.user)
            except InvalidTransitionError as e:
                logger.warning(f"Could not auto-transition application {pk}: {e}")

        serializer = AdminApplicationDetailSerializer(application, context={'request': request})
        return Response(serializer.data)


@extend_schema(tags=['Admin'])
class ApproveApplicationView(APIView):
    """Approve an application in UNDER_REVIEW status."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(request=ApproveSerializer, responses={200: AdminApplicationDetailSerializer})
    def post(self, request, pk):
        application = get_object_or_404(DriverApplication, id=pk)
        serializer = ApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        note = serializer.validated_data.get('note', '')

        try:
            state_machine.transition(application, 'APPROVED', actor=request.user, note=note)
        except InvalidTransitionError as e:
            return Response(
                {'error': True, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(f"Application {pk} approved by {request.user.phone_number}")
        return Response(AdminApplicationDetailSerializer(application, context={'request': request}).data)


@extend_schema(tags=['Admin'])
class RejectApplicationView(APIView):
    """Reject an application in UNDER_REVIEW status (reason required)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(request=RejectSerializer, responses={200: AdminApplicationDetailSerializer})
    def post(self, request, pk):
        application = get_object_or_404(DriverApplication, id=pk)
        serializer = RejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reason = serializer.validated_data['reason']

        try:
            state_machine.transition(application, 'REJECTED', actor=request.user, note=reason)
        except InvalidTransitionError as e:
            return Response(
                {'error': True, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(f"Application {pk} rejected by {request.user.phone_number}")
        return Response(AdminApplicationDetailSerializer(application, context={'request': request}).data)


@extend_schema(tags=['Admin'])
class AdminStatisticsView(APIView):
    """Return aggregate application counts by status."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        counts = (
            DriverApplication.objects
            .values('status')
            .annotate(count=Count('id'))
        )
        stats = {row['status']: row['count'] for row in counts}
        total = sum(stats.values())

        return Response({
            'total': total,
            'DRAFT': stats.get('DRAFT', 0),
            'SUBMITTED': stats.get('SUBMITTED', 0),
            'UNDER_REVIEW': stats.get('UNDER_REVIEW', 0),
            'APPROVED': stats.get('APPROVED', 0),
            'REJECTED': stats.get('REJECTED', 0),
        })
