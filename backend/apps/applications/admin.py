from django.contrib import admin
from .models import DriverApplication, ApplicationStatusHistory, ApplicationSequence


class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ('id', 'previous_status', 'new_status', 'changed_by', 'note', 'created_at')
    can_delete = False


@admin.register(DriverApplication)
class DriverApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_reference', 'driver', 'status', 'submitted_at', 'reviewed_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('application_reference', 'driver__phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'application_reference', 'created_at', 'updated_at')
    inlines = [ApplicationStatusHistoryInline]


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'previous_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('new_status',)
    search_fields = ('application__application_reference',)
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')


@admin.register(ApplicationSequence)
class ApplicationSequenceAdmin(admin.ModelAdmin):
    list_display = ('year', 'last_sequence')
