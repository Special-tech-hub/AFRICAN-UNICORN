"""Views for document upload, listing, deletion, and secure serving."""
import logging
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from core.permissions import IsDriverUser, IsPhoneVerified
from apps.applications.models import DriverApplication
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .storage import generate_safe_filename

logger = logging.getLogger(__name__)


@extend_schema(tags=['Documents'])
class DocumentListCreateView(APIView):
    """List driver documents or upload a new one."""
    permission_classes = [IsAuthenticated, IsDriverUser, IsPhoneVerified]

    @extend_schema(responses={200: DocumentSerializer(many=True)})
    def get(self, request):
        docs = Document.objects.filter(driver=request.user).order_by('-uploaded_at')
        return Response(DocumentSerializer(docs, many=True, context={'request': request}).data)

    @extend_schema(request=DocumentUploadSerializer, responses={201: DocumentSerializer})
    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        document_type = serializer.validated_data['document_type']
        detected_mime = serializer.validated_data['detected_mime']

        original_filename = file.name
        safe_name = generate_safe_filename(original_filename)
        application = DriverApplication.objects.filter(driver=request.user).first()

        # Rename file to safe UUID name before saving
        file.name = safe_name

        doc = Document(
            driver=request.user,
            application=application,
            document_type=document_type,
            original_filename=original_filename,
            safe_filename=safe_name,
            file_size=file.size,
            mime_type=detected_mime,
            file=file,
        )
        doc.save()

        logger.info(f"Document uploaded: {document_type} for {request.user.phone_number}")
        return Response(
            DocumentSerializer(doc, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Documents'])
class DocumentDeleteView(APIView):
    """Delete an uploaded document (DRAFT applications only)."""
    permission_classes = [IsAuthenticated, IsDriverUser]

    def delete(self, request, pk):
        doc = get_object_or_404(Document, id=pk, driver=request.user)

        if doc.application and doc.application.status != DriverApplication.STATUS_DRAFT:
            return Response(
                {'error': True, 'message': 'Documents cannot be deleted after submission.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            if doc.file:
                doc.file.delete(save=False)
        except Exception as e:
            logger.warning(f"Could not delete file for document {pk}: {e}")

        doc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Documents'])
class DocumentServeView(APIView):
    """Serve a document file with JWT auth and ownership check."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        doc = get_object_or_404(Document, id=pk)

        is_owner = doc.driver == request.user
        is_admin = request.user.role == 'ADMIN'
        if not (is_owner or is_admin):
            return Response(
                {'error': True, 'message': 'Access denied.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            file_handle = doc.file.open('rb')
            return FileResponse(
                file_handle,
                content_type=doc.mime_type,
                as_attachment=False,
                filename=doc.original_filename,
            )
        except FileNotFoundError:
            return Response(
                {'error': True, 'message': 'Document file not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
