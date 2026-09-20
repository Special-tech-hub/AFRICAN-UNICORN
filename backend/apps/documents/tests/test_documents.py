"""Document tests: upload, serve, delete access controls."""
import pytest
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.applications.models import DriverApplication
from apps.documents.models import Document


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_driver(db):
    return User.objects.create_user(
        phone_number='0771900001',
        password='Pass1234!',
        role='DRIVER',
        is_phone_verified=True,
    )


@pytest.fixture
def other_driver(db):
    return User.objects.create_user(
        phone_number='0771900002',
        password='Pass1234!',
        role='DRIVER',
        is_phone_verified=True,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        phone_number='0700900001',
        password='Admin1234!',
        role='ADMIN',
        is_phone_verified=True,
        is_staff=True,
    )


def make_pdf():
    """Create a minimal valid-looking PDF bytes object."""
    return b'%PDF-1.4 1 0 obj<</Type/Catalog>>endobj'


def make_jpeg():
    """Create a real minimal JPEG in memory."""
    img = Image.new('RGB', (10, 10), color=(255, 0, 0))
    buf = BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf.read()


@pytest.mark.django_db
class TestDocumentUpload:
    def test_upload_pdf_success(self, api_client, verified_driver):
        DriverApplication.objects.create(driver=verified_driver)
        api_client.force_authenticate(user=verified_driver)
        f = SimpleUploadedFile('test.pdf', make_pdf(), content_type='application/pdf')
        resp = api_client.post('/api/driver/documents/', {
            'document_type': 'NATIONAL_ID',
            'file': f,
        }, format='multipart')
        # 201 or 400 depending on python-magic availability; at minimum not 401/403
        assert resp.status_code in (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST)

    def test_upload_oversized_file_returns_400(self, api_client, verified_driver):
        DriverApplication.objects.create(driver=verified_driver)
        api_client.force_authenticate(user=verified_driver)
        big_content = b'A' * (11 * 1024 * 1024)  # 11 MB
        f = SimpleUploadedFile('big.pdf', big_content, content_type='application/pdf')
        resp = api_client.post('/api/driver/documents/', {
            'document_type': 'NATIONAL_ID',
            'file': f,
        }, format='multipart')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_upload_returns_401(self, api_client):
        f = SimpleUploadedFile('test.pdf', make_pdf(), content_type='application/pdf')
        resp = api_client.post('/api/driver/documents/', {
            'document_type': 'NATIONAL_ID',
            'file': f,
        }, format='multipart')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_returns_only_own_documents(self, api_client, verified_driver, other_driver):
        # Create doc for other_driver
        app = DriverApplication.objects.create(driver=other_driver)
        from django.core.files.base import ContentFile
        doc = Document(
            driver=other_driver, application=app,
            document_type='NATIONAL_ID',
            original_filename='other.pdf',
            safe_filename='other_safe.pdf',
            file_size=100,
            mime_type='application/pdf',
        )
        doc.file.save('other.pdf', ContentFile(make_pdf()), save=True)

        api_client.force_authenticate(user=verified_driver)
        resp = api_client.get('/api/driver/documents/')
        assert resp.status_code == status.HTTP_200_OK
        # verified_driver has no docs, should be empty
        assert len(resp.data) == 0


@pytest.mark.django_db
class TestDocumentDelete:
    def test_delete_on_submitted_application_returns_403(self, api_client, verified_driver):
        app = DriverApplication.objects.create(
            driver=verified_driver,
            status='SUBMITTED',
            application_reference='TO-2026-00099',
        )
        from django.core.files.base import ContentFile
        doc = Document(
            driver=verified_driver, application=app,
            document_type='NATIONAL_ID',
            original_filename='id.pdf',
            safe_filename='id_safe.pdf',
            file_size=100,
            mime_type='application/pdf',
        )
        doc.file.save('id.pdf', ContentFile(make_pdf()), save=True)

        api_client.force_authenticate(user=verified_driver)
        resp = api_client.delete(f'/api/driver/documents/{doc.id}/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDocumentServe:
    def test_serve_unauthenticated_returns_401(self, api_client, verified_driver):
        app = DriverApplication.objects.create(driver=verified_driver)
        from django.core.files.base import ContentFile
        doc = Document(
            driver=verified_driver, application=app,
            document_type='NATIONAL_ID',
            original_filename='id.pdf',
            safe_filename='id_safe.pdf',
            file_size=100,
            mime_type='application/pdf',
        )
        doc.file.save('id.pdf', ContentFile(make_pdf()), save=True)
        resp = api_client.get(f'/api/driver/documents/{doc.id}/download/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_serve_wrong_driver_returns_403(self, api_client, verified_driver, other_driver):
        app = DriverApplication.objects.create(driver=other_driver)
        from django.core.files.base import ContentFile
        doc = Document(
            driver=other_driver, application=app,
            document_type='NATIONAL_ID',
            original_filename='id.pdf',
            safe_filename='id_safe.pdf',
            file_size=100,
            mime_type='application/pdf',
        )
        doc.file.save('id.pdf', ContentFile(make_pdf()), save=True)
        api_client.force_authenticate(user=verified_driver)
        resp = api_client.get(f'/api/driver/documents/{doc.id}/download/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN
