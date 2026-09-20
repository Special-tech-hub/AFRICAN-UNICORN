"""Serializers for driver applications and status history."""
from rest_framework import serializers
from .models import DriverApplication, ApplicationStatusHistory


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_role = serializers.SerializerMethodField()
    changed_by_phone = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationStatusHistory
        fields = (
            'id', 'previous_status', 'new_status',
            'changed_by_role', 'changed_by_phone',
            'note', 'created_at',
        )
        read_only_fields = fields

    def get_changed_by_role(self, obj):
        return obj.changed_by.role if obj.changed_by else None

    def get_changed_by_phone(self, obj):
        # Only expose admin phone to admins; otherwise omit
        if obj.changed_by and obj.changed_by.role == 'ADMIN':
            return obj.changed_by.phone_number
        return None


class DriverApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverApplication
        fields = (
            'id', 'application_reference', 'status',
            'submitted_at', 'reviewed_at', 'review_note', 'created_at',
        )
        read_only_fields = fields


class ApplicationStatusSerializer(serializers.ModelSerializer):
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = DriverApplication
        fields = (
            'id', 'application_reference', 'status',
            'submitted_at', 'reviewed_at', 'review_note',
            'status_history',
        )
        read_only_fields = fields
