from django.contrib import admin

from .models import ReportExport


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ("id", "survey", "created_by", "status", "created_at")
    list_filter = ("status", "created_at", "survey")
    readonly_fields = ("file", "created_at", "completed_at", "error_message")
