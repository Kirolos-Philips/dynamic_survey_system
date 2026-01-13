from rest_framework import serializers

from .models import ReportExport


class ReportExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = [
            "id",
            "survey",
            "created_by",
            "status",
            "file",
            "created_at",
            "completed_at",
            "error_message",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "status",
            "file",
            "created_at",
            "completed_at",
            "error_message",
        ]
