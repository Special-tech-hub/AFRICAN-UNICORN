"""URL configuration for admin review endpoints."""
from django.urls import path
from .views import (
    AdminApplicationListView,
    AdminApplicationDetailView,
    ApproveApplicationView,
    RejectApplicationView,
    AdminStatisticsView,
)

app_name = 'reviews'

urlpatterns = [
    path('applications/', AdminApplicationListView.as_view(), name='application-list'),
    path('applications/<uuid:pk>/', AdminApplicationDetailView.as_view(), name='application-detail'),
    path('applications/<uuid:pk>/approve/', ApproveApplicationView.as_view(), name='approve'),
    path('applications/<uuid:pk>/reject/', RejectApplicationView.as_view(), name='reject'),
    path('statistics/', AdminStatisticsView.as_view(), name='statistics'),
]
