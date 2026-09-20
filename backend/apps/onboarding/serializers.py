"""Serializers for driver onboarding: profile, identity, vehicle."""
from datetime import date
from rest_framework import serializers
from .models import DriverProfile, IdentityVerification, Vehicle


class DriverProfileSerializer(serializers.ModelSerializer):
    """Serializer for driver personal and contact details."""

    class Meta:
        model = DriverProfile
        fields = (
            'id', 'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'gender', 'nationality',
            'email', 'street_address', 'city', 'province',
            'emergency_contact_name', 'emergency_contact_phone',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_date_of_birth(self, value):
        if value is None:
            return value
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 16:
            raise serializers.ValidationError("Driver must be at least 16 years old.")
        if age > 100:
            raise serializers.ValidationError("Please enter a valid date of birth.")
        if value > today:
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_email(self, value):
        if value and '@' not in value:
            raise serializers.ValidationError("Enter a valid email address.")
        return value


class IdentityVerificationSerializer(serializers.ModelSerializer):
    """Serializer for identity and driving licence details."""

    is_license_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = IdentityVerification
        fields = (
            'id', 'id_type', 'id_number',
            'drivers_license_number', 'license_expiry_date', 'is_license_expired',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'is_license_expired', 'created_at', 'updated_at')

    def validate_id_type(self, value):
        valid_types = [choice[0] for choice in IdentityVerification.ID_TYPE_CHOICES]
        if value and value not in valid_types:
            raise serializers.ValidationError(f"ID type must be one of: {', '.join(valid_types)}")
        return value

    def validate_license_expiry_date(self, value):
        if value is None:
            return value
        if value < date(1900, 1, 1):
            raise serializers.ValidationError("Enter a valid licence expiry date.")
        return value


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for vehicle details."""

    class Meta:
        model = Vehicle
        fields = (
            'id', 'vehicle_type', 'make', 'model', 'year',
            'registration_number', 'colour',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_vehicle_type(self, value):
        valid_types = [choice[0] for choice in Vehicle.TYPE_CHOICES]
        if value and value not in valid_types:
            raise serializers.ValidationError(f"Vehicle type must be one of: {', '.join(valid_types)}")
        return value

    def validate_year(self, value):
        if value is None:
            return value
        current_year = date.today().year
        if value < 1900:
            raise serializers.ValidationError("Vehicle year cannot be before 1900.")
        if value > current_year + 1:
            raise serializers.ValidationError(f"Vehicle year cannot be after {current_year + 1}.")
        return value

    def validate_registration_number(self, value):
        if value is not None and not value.strip():
            raise serializers.ValidationError("Registration number cannot be blank.")
        return value
