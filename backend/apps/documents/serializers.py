"""Serializers for document upload and retrieval."""
from rest_framework import serializers
from .models import Document
from .validators import MIMEValidator, ExtensionValidator, FileSizeValidator


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for uploading a new document."""
    document_type = serializers.ChoiceField(choices=Document.DOCUMENT_TYPE_CHOICES)
    file = serializers.FileField()

    def validate(self, attrs):
        file = attrs['file']
        size_validator = FileSizeValidator()
        mime_validator = MIMEValidator()
        ext_validator = ExtensionValidator()

        # Validate file size first
        size_validator(file)

        # Validate MIME type from file bytes
        detected_mime = mime_validator(file)

        # Validate extension matches MIME
        ext_validator(file, detected_mime)

        attrs['detected_mime'] = detected_mime
        return attrs


class DocumentSerializer(serializers.ModelSerializer):
    """Read-only serializer for document metadata with download URL."""
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id', 'document_type', 'original_filename',
            'file_size', 'mime_type', 'verification_status',
            'uploaded_at', 'download_url',
        )
        read_only_fields = fields

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/driver/documents/{obj.id}/download/')
        return f'/api/driver/documents/{obj.id}/download/'
