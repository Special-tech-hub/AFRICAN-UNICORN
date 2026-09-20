from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'email', 'role', 'is_phone_verified', 'is_active', 'created_at')
    list_filter = ('role', 'is_phone_verified', 'is_active', 'is_staff')
    search_fields = ('phone_number', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('id', 'phone_number', 'password')}),
        ('Personal Info', {'fields': ('email',)}),
        ('Role & Status', {'fields': ('role', 'is_phone_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'attempt_count', 'expires_at', 'verified_at', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__phone_number',)
    ordering = ('-created_at',)
    readonly_fields = ('id', 'otp_hash', 'otp_salt', 'created_at')
