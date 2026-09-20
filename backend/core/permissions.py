"""
Custom DRF permissions for TakeOFF Driver Onboarding Platform.
"""
from rest_framework.permissions import BasePermission


class IsDriverUser(BasePermission):
    """Allow access only to users with DRIVER role."""

    message = 'Access restricted to drivers only.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'DRIVER'
        )


class IsAdminUser(BasePermission):
    """Allow access only to users with ADMIN role."""

    message = 'Access restricted to administrators only.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsPhoneVerified(BasePermission):
    """Allow access only to users who have verified their phone number."""

    message = 'Phone number verification required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_phone_verified
        )


class IsOwnerOrAdmin(BasePermission):
    """Allow access to the object owner or any admin user."""

    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated and request.user.role == 'ADMIN':
            return True
        # Check common owner field patterns
        if hasattr(obj, 'driver'):
            return obj.driver == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
