"""URL configuration for accounts (authentication) endpoints."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    OTPResendView,
    OTPVerifyView,
    RegisterView,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('resend-otp/', OTPResendView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
