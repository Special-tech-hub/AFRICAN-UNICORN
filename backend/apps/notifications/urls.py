"""URL configuration for notification endpoints."""
from django.urls import path
from .views import NotificationListView, MarkNotificationReadView

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('<uuid:pk>/read/', MarkNotificationReadView.as_view(), name='mark-read'),
]
