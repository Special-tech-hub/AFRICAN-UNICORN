"""
Management command: create_admin
Creates an admin user from command-line arguments.
Use for production bootstrap without running seed_data.

Usage: python manage.py create_admin --phone 0700000000 --password AdminPass123!
"""
from django.core.management.base import BaseCommand, CommandError
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create an admin user for production bootstrap.'

    def add_arguments(self, parser):
        parser.add_argument('--phone', required=True, help='Admin phone number')
        parser.add_argument('--password', required=True, help='Admin password')
        parser.add_argument('--email', default='', help='Admin email (optional)')

    def handle(self, *args, **options):
        phone = options['phone']
        password = options['password']
        email = options.get('email', '')

        if User.objects.filter(phone_number=phone).exists():
            raise CommandError(f"A user with phone number '{phone}' already exists.")

        if len(password) < 8:
            raise CommandError("Password must be at least 8 characters.")

        admin = User.objects.create_user(
            phone_number=phone,
            password=password,
            role='ADMIN',
            is_phone_verified=True,
            is_staff=True,
            is_superuser=True,
            email=email or None,
        )

        self.stdout.write(self.style.SUCCESS(
            f"Admin user created successfully!\n"
            f"  Phone: {admin.phone_number}\n"
            f"  Role: {admin.role}\n"
            f"  ID: {admin.id}"
        ))
