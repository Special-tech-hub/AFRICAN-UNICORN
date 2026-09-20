"""
Serializers for accounts app: Registration, OTP, Login.
"""
import re
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, normalize_phone_number, phone_number_variants
from .services import OTPService
from .exceptions import OTPCooldownError


class RegisterSerializer(serializers.Serializer):
    """Validates driver registration data."""

    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate_phone_number(self, value):
        normalized = normalize_phone_number(value)
        if not re.match(r'^0\d{9,10}$', normalized):
            raise serializers.ValidationError("Enter a valid phone number.")

        lookup_values = set(phone_number_variants(value))
        if User.objects.filter(phone_number__in=list(lookup_values)).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return normalized

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class OTPVerifySerializer(serializers.Serializer):
    """Validates OTP verification submission."""
    phone_number = serializers.CharField(max_length=20)
    otp = serializers.CharField(min_length=6, max_length=6)

    def validate_phone_number(self, value):
        normalized = normalize_phone_number(value)
        if not re.match(r'^0\d{9,10}$', normalized):
            raise serializers.ValidationError("Enter a valid phone number.")
        return normalized


class OTPResendSerializer(serializers.Serializer):
    """Validates OTP resend request."""
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        normalized = normalize_phone_number(value)
        lookup_values = set(phone_number_variants(value))
        if not User.objects.filter(phone_number__in=list(lookup_values)).exists():
            raise serializers.ValidationError("No account found for this phone number.")
        return normalized


class LoginSerializer(serializers.Serializer):
    """Validates login credentials and checks phone verification."""
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate_phone_number(self, value):
        return normalize_phone_number(value)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = authenticate(username=phone_number, password=password)
        if user is None:
            for candidate in phone_number_variants(phone_number):
                user = authenticate(username=candidate, password=password)
                if user is not None:
                    attrs['user'] = user
                    return attrs

        if user is None:
            raise serializers.ValidationError(
                {'non_field_errors': 'Invalid phone number or password.'}
            )

        if not user.is_phone_verified:
            raise serializers.ValidationError(
                {'non_field_errors': 'Please verify your phone number before logging in.'},
                code='phone_not_verified',
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {'non_field_errors': 'This account has been deactivated.'}
            )

        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    """Validates logout request containing refresh token."""
    refresh = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Read-only serializer for user info returned in auth responses."""

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'role', 'is_phone_verified', 'created_at')
        read_only_fields = fields
