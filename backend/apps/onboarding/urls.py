"""URL configuration for driver onboarding endpoints."""
from django.urls import path
from .views import DriverProfileView, IdentityVerificationView, VehicleView

app_name = 'onboarding'

urlpatterns = [
    path('profile/', DriverProfileView.as_view(), name='profile'),
    path('identity/', IdentityVerificationView.as_view(), name='identity'),
    path('vehicle/', VehicleView.as_view(), name='vehicle'),
]
