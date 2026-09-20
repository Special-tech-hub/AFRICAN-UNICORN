"""Serializers for admin review: application list, detail, approve, reject."""
from rest_framework import serializers
from apps.applications.models import DriverApplication, ApplicationStatusHistory
from apps.onboarding.models import DriverProfile, IdentityVerification, Vehicle
from apps.documents.models import Document


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_role = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationStatusHistory
        fields = ('previous_status', 'new_status', 'changed_by_role', 'note', 'created_at')

    def get_changed_by_role(self, obj):
        return obj.changed_by.role if obj.changed_by else None


class AdminApplicationListSerializer(serializers.ModelSerializer):
    """Compact serializer for the application list view."""
    driver_name = serializers.SerializerMethodField()
    driver_phone = serializers.SerializerMethodField()
    vehicle_summary = serializers.SerializerMethodField()
    reviewer_phone = serializers.SerializerMethodField()

    class Meta:
        model = DriverApplication
        fields = (
            'id', 'application_reference', 'driver_name', 'driver_phone',
            'vehicle_summary', 'submitted_at', 'status', 'reviewer_phone', 'created_at',
        )

    def get_driver_name(self, obj):
        try:
            p = obj.driver.driver_profile
            return f"{p.first_name} {p.last_name}".strip() or obj.driver.phone_number
        except Exception:
            return obj.driver.phone_number

    def get_driver_phone(self, obj):
        return obj.driver.phone_number

    def get_vehicle_summary(self, obj):
        try:
            v = obj.driver.vehicle
            return f"{v.make} {v.model} ({v.vehicle_type})"
        except Exception:
            return None

    def get_reviewer_phone(self, obj):
        return obj.reviewed_by.phone_number if obj.reviewed_by else None


class DriverProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = (
            'first_name', 'middle_name', 'last_name', 'date_of_birth',
            'gender', 'nationality', 'email', 'street_address', 'city', 'province',
            'emergency_contact_name', 'emergency_contact_phone',
        )


class IdentityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityVerification
        fields = (
            'id_type', 'id_number', 'drivers_license_number',
            'license_expiry_date', 'is_license_expired',
        )


class VehicleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('vehicle_type', 'make', 'model', 'year', 'registration_number', 'colour')


class DocumentDetailSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id', 'document_type', 'original_filename',
            'file_size', 'mime_type', 'verification_status',
            'uploaded_at', 'download_url',
        )

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/driver/documents/{obj.id}/download/')
        return f'/api/driver/documents/{obj.id}/download/'


class AdminApplicationDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for admin review page."""
    profile = serializers.SerializerMethodField()
    identity = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    driver_phone = serializers.SerializerMethodField()

    class Meta:
        model = DriverApplication
        fields = (
            'id', 'application_reference', 'status',
            'submitted_at', 'reviewed_at', 'review_note',
            'driver_phone', 'profile', 'identity', 'vehicle',
            'documents', 'status_history', 'created_at',
        )

    def get_driver_phone(self, obj):
        return obj.driver.phone_number

    def get_profile(self, obj):
        try:
            return DriverProfileDetailSerializer(obj.driver.driver_profile).data
        except Exception:
            return None

    def get_identity(self, obj):
        try:
            return IdentityDetailSerializer(obj.driver.identity_verification).data
        except Exception:
            return None

    def get_vehicle(self, obj):
        try:
            return VehicleDetailSerializer(obj.driver.vehicle).data
        except Exception:
            return None

    def get_documents(self, obj):
        docs = Document.objects.filter(driver=obj.driver)
        return DocumentDetailSerializer(
            docs, many=True, context=self.context
        ).data


class ApproveSerializer(serializers.Serializer):
    """Serializer for application approval — optional note."""
    note = serializers.CharField(required=False, allow_blank=True, default='')


class RejectSerializer(serializers.Serializer):
    """Serializer for application rejection — reason is required."""
    reason = serializers.CharField(min_length=1, error_messages={
        'blank': 'A rejection reason is required.',
        'required': 'A rejection reason is required.',
    })
