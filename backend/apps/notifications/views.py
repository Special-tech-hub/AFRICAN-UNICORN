"""Views for listing and marking notifications as read."""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Notification
from .serializers import NotificationSerializer


@extend_schema(tags=['Notifications'])
class NotificationListView(APIView):
    """List all notifications for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: NotificationSerializer(many=True)})
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        return Response(NotificationSerializer(notifications, many=True).data)


@extend_schema(tags=['Notifications'])
class MarkNotificationReadView(APIView):
    """Mark a notification as read."""
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: NotificationSerializer})
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)
