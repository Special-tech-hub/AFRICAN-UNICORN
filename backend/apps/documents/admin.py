from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('driver', 'document_type', 'original_filename', 'file_size', 'verification_status', 'uploaded_at')
    list_filter = ('document_type', 'verification_status')
    search_fields = ('driver__phone_number', 'original_filename', 'document_type')
    ordering = ('-uploaded_at',)
    readonly_fields = ('id', 'safe_filename', 'mime_type', 'file_size', 'uploaded_at')
