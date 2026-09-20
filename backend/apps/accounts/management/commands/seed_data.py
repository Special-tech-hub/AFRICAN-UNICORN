"""
Management command: seed_data
Creates fictional test data for all application statuses.
Safe to run multiple times (idempotent).

Usage: python manage.py seed_data
"""
import io
import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Seed the database with fictional test driver data covering all application statuses.'

    ADMIN = {
        'phone_number': '0700000000',
        'password': 'Admin1234!',
        'role': 'ADMIN',
        'is_phone_verified': True,
        'is_staff': True,
    }

    DRIVERS = [
        {
            'phone_number': '0771100001',
            'password': 'Driver001!',
            'email': 'tendai.moyo@example.com',
            'target_status': 'APPROVED',
            'profile': {
                'first_name': 'Tendai', 'last_name': 'Moyo',
                'date_of_birth': date(1990, 3, 15),
                'gender': 'MALE', 'nationality': 'Zimbabwean',
                'email': 'tendai.moyo@example.com',
                'street_address': '12 Samora Machel Ave', 'city': 'Harare', 'province': 'Harare',
                'emergency_contact_name': 'Grace Moyo', 'emergency_contact_phone': '0771200001',
            },
            'identity': {
                'id_type': 'NATIONAL_ID', 'id_number': 'TEST-NID-001',
                'drivers_license_number': 'TEST-DL-001',
                'license_expiry_date': date(2028, 6, 30),
            },
            'vehicle': {
                'vehicle_type': 'SEDAN', 'make': 'Toyota', 'model': 'Corolla',
                'year': 2020, 'registration_number': 'TEST-1234', 'colour': 'White',
            },
            'review_note': 'All documents verified. Approved.',
        },
        {
            'phone_number': '0771100002',
            'password': 'Driver002!',
            'email': 'amara.diallo@example.com',
            'target_status': 'REJECTED',
            'profile': {
                'first_name': 'Amara', 'last_name': 'Diallo',
                'date_of_birth': date(1995, 7, 22),
                'gender': 'FEMALE', 'nationality': 'Ghanaian',
                'email': 'amara.diallo@example.com',
                'street_address': '5 Independence Ave', 'city': 'Accra', 'province': 'Greater Accra',
                'emergency_contact_name': 'Kwame Diallo', 'emergency_contact_phone': '0771200002',
            },
            'identity': {
                'id_type': 'PASSPORT', 'id_number': 'TEST-PASS-002',
                'drivers_license_number': 'TEST-DL-002',
                'license_expiry_date': date(2023, 1, 15),  # Expired
            },
            'vehicle': {
                'vehicle_type': 'MOTORCYCLE', 'make': 'Honda', 'model': 'CB150',
                'year': 2019, 'registration_number': 'TEST-5678', 'colour': 'Red',
            },
            'review_note': 'Driver licence has expired. Please renew and reapply.',
        },
        {
            'phone_number': '0771100003',
            'password': 'Driver003!',
            'email': 'kofi.asante@example.com',
            'target_status': 'UNDER_REVIEW',
            'profile': {
                'first_name': 'Kofi', 'last_name': 'Asante',
                'date_of_birth': date(1988, 11, 5),
                'gender': 'MALE', 'nationality': 'Kenyan',
                'email': 'kofi.asante@example.com',
                'street_address': '88 Kenyatta Road', 'city': 'Nairobi', 'province': 'Nairobi',
                'emergency_contact_name': 'Aisha Asante', 'emergency_contact_phone': '0771200003',
            },
            'identity': {
                'id_type': 'NATIONAL_ID', 'id_number': 'TEST-NID-003',
                'drivers_license_number': 'TEST-DL-003',
                'license_expiry_date': date(2027, 3, 20),
            },
            'vehicle': {
                'vehicle_type': 'PICKUP', 'make': 'Ford', 'model': 'Ranger',
                'year': 2021, 'registration_number': 'TEST-9012', 'colour': 'Blue',
            },
            'review_note': '',
        },
        {
            'phone_number': '0771100004',
            'password': 'Driver004!',
            'email': 'fatima.nkosi@example.com',
            'target_status': 'SUBMITTED',
            'profile': {
                'first_name': 'Fatima', 'last_name': 'Nkosi',
                'date_of_birth': date(1993, 5, 18),
                'gender': 'FEMALE', 'nationality': 'South African',
                'email': 'fatima.nkosi@example.com',
                'street_address': '22 Nelson Mandela Drive', 'city': 'Johannesburg', 'province': 'Gauteng',
                'emergency_contact_name': 'Sipho Nkosi', 'emergency_contact_phone': '0771200004',
            },
            'identity': {
                'id_type': 'NATIONAL_ID', 'id_number': 'TEST-NID-004',
                'drivers_license_number': 'TEST-DL-004',
                'license_expiry_date': date(2026, 9, 10),
            },
            'vehicle': {
                'vehicle_type': 'VAN', 'make': 'Volkswagen', 'model': 'Transporter',
                'year': 2018, 'registration_number': 'TEST-3456', 'colour': 'Silver',
            },
            'review_note': '',
        },
        {
            'phone_number': '0771100005',
            'password': 'Driver005!',
            'email': 'chidi.okafor@example.com',
            'target_status': 'DRAFT',
            'profile': {
                'first_name': 'Chidi', 'last_name': 'Okafor',
                'date_of_birth': date(1998, 2, 28),
                'gender': 'MALE', 'nationality': 'Nigerian',
                'email': 'chidi.okafor@example.com',
                'street_address': '7 Adeola Odeku Street', 'city': 'Lagos', 'province': 'Lagos',
                'emergency_contact_name': 'Ngozi Okafor', 'emergency_contact_phone': '0771200005',
            },
            'identity': {
                'id_type': 'PASSPORT', 'id_number': 'TEST-PASS-005',
                'drivers_license_number': 'TEST-DL-005',
                'license_expiry_date': date(2029, 12, 31),
            },
            'vehicle': {
                'vehicle_type': 'HATCHBACK', 'make': 'Hyundai', 'model': 'i20',
                'year': 2022, 'registration_number': 'TEST-7890', 'colour': 'Black',
            },
            'review_note': '',
        },
    ]

    def handle(self, *args, **options):
        from apps.accounts.models import User
        from apps.onboarding.models import DriverProfile, IdentityVerification, Vehicle
        from apps.documents.models import Document
        from apps.applications.models import DriverApplication, ApplicationStatusHistory
        from apps.applications.reference import generate_application_reference

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding TakeOFF database...'))

        # Create admin
        admin, created = User.objects.get_or_create(
            phone_number=self.ADMIN['phone_number'],
            defaults={
                'role': 'ADMIN',
                'is_phone_verified': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin.role = 'ADMIN'
        admin.is_phone_verified = True
        admin.is_staff = True
        admin.is_superuser = True
        admin.email = admin.email or None
        admin.set_password(self.ADMIN['password'])
        admin.save()

        if created:
            self.stdout.write(f'  Created admin: {admin.phone_number}')
        else:
            self.stdout.write(f'  Admin already exists: {admin.phone_number}')

        # Create fake PDF content for documents
        fake_pdf = b'%PDF-1.4 fake test document content'

        results = []
        for driver_data in self.DRIVERS:
            phone = driver_data['phone_number']
            target_status = driver_data['target_status']

            # Create user
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={'role': 'DRIVER', 'is_phone_verified': True, 'email': driver_data['email']},
            )
            user.role = 'DRIVER'
            user.is_phone_verified = True
            user.email = driver_data['email']
            user.set_password(driver_data['password'])
            user.save()

            if created:
                self.stdout.write(f'  Created driver: {user.phone_number}')

            # Create profile
            profile_data = driver_data['profile']
            DriverProfile.objects.update_or_create(user=user, defaults=profile_data)

            # Create identity
            identity_data = driver_data['identity']
            IdentityVerification.objects.update_or_create(driver=user, defaults=identity_data)

            # Create vehicle
            vehicle_data = driver_data['vehicle']
            Vehicle.objects.update_or_create(driver=user, defaults=vehicle_data)

            # Create application if not DRAFT
            app, app_created = DriverApplication.objects.get_or_create(
                driver=user,
                defaults={'status': 'DRAFT'},
            )

            # Upload placeholder documents for non-DRAFT
            if target_status != 'DRAFT':
                for doc_type in ['NATIONAL_ID', 'DRIVERS_LICENSE', 'VEHICLE_REGISTRATION', 'INSURANCE']:
                    if not Document.objects.filter(driver=user, document_type=doc_type).exists():
                        doc = Document(
                            driver=user,
                            application=app,
                            document_type=doc_type,
                            original_filename=f'{doc_type.lower()}_test.pdf',
                            safe_filename=f'test_{doc_type.lower()}.pdf',
                            file_size=len(fake_pdf),
                            mime_type='application/pdf',
                        )
                        doc.file.save(
                            f'test_{doc_type.lower()}.pdf',
                            ContentFile(fake_pdf),
                            save=False,
                        )
                        doc.save()

            # Advance application status
            if target_status != 'DRAFT' and app.status == 'DRAFT':
                # DRAFT → SUBMITTED
                from apps.applications.reference import generate_application_reference
                if not app.application_reference:
                    app.application_reference = generate_application_reference()
                app.status = 'SUBMITTED'
                app.submitted_at = timezone.now() - timedelta(days=5)
                app.save()
                ApplicationStatusHistory.objects.get_or_create(
                    application=app, new_status='SUBMITTED',
                    defaults={'previous_status': 'DRAFT', 'changed_by': user, 'note': ''},
                )

            if target_status in ('UNDER_REVIEW', 'APPROVED', 'REJECTED') and app.status == 'SUBMITTED':
                app.status = 'UNDER_REVIEW'
                app.save()
                ApplicationStatusHistory.objects.get_or_create(
                    application=app, new_status='UNDER_REVIEW',
                    defaults={'previous_status': 'SUBMITTED', 'changed_by': admin, 'note': ''},
                )

            if target_status == 'APPROVED' and app.status == 'UNDER_REVIEW':
                app.status = 'APPROVED'
                app.reviewed_at = timezone.now() - timedelta(days=1)
                app.reviewed_by = admin
                app.review_note = driver_data.get('review_note', '')
                app.save()
                ApplicationStatusHistory.objects.get_or_create(
                    application=app, new_status='APPROVED',
                    defaults={
                        'previous_status': 'UNDER_REVIEW', 'changed_by': admin,
                        'note': driver_data.get('review_note', ''),
                    },
                )

            if target_status == 'REJECTED' and app.status == 'UNDER_REVIEW':
                app.status = 'REJECTED'
                app.reviewed_at = timezone.now() - timedelta(days=2)
                app.reviewed_by = admin
                app.review_note = driver_data.get('review_note', 'Application rejected.')
                app.save()
                ApplicationStatusHistory.objects.get_or_create(
                    application=app, new_status='REJECTED',
                    defaults={
                        'previous_status': 'UNDER_REVIEW', 'changed_by': admin,
                        'note': driver_data.get('review_note', 'Application rejected.'),
                    },
                )

            results.append({
                'phone': phone,
                'name': f"{driver_data['profile']['first_name']} {driver_data['profile']['last_name']}",
                'status': app.status,
                'ref': app.application_reference or 'N/A',
            })

        # Print summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
        self.stdout.write('=' * 60)
        self.stdout.write(f"{'Phone':<15} {'Name':<20} {'Status':<15} {'Reference':<15}")
        self.stdout.write('-' * 65)
        for r in results:
            self.stdout.write(f"{r['phone']:<15} {r['name']:<20} {r['status']:<15} {r['ref']:<15}")
        self.stdout.write('=' * 60)
        self.stdout.write(f"\nAdmin: {self.ADMIN['phone_number']} / {self.ADMIN['password']}")
        self.stdout.write('Driver passwords follow the pattern: Driver001!, Driver002!, etc.')
