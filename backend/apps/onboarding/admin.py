from django.contrib import admin
from .models import DriverProfile, IdentityVerification, Vehicle


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'gender', 'nationality', 'city', 'created_at')
    list_filter = ('gender', 'nationality')
    search_fields = ('user__phone_number', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(IdentityVerification)
class IdentityVerificationAdmin(admin.ModelAdmin):
    list_display = ('driver', 'id_type', 'id_number', 'license_expiry_date', 'is_license_expired', 'created_at')
    list_filter = ('id_type', 'is_license_expired')
    search_fields = ('driver__phone_number', 'id_number', 'drivers_license_number')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'is_license_expired', 'created_at', 'updated_at')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('driver', 'vehicle_type', 'make', 'model', 'year', 'registration_number', 'colour')
    list_filter = ('vehicle_type',)
    search_fields = ('driver__phone_number', 'registration_number', 'make', 'model')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
