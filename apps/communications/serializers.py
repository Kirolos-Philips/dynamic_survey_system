from rest_framework import serializers

from .models import InvitationBatch


class InvitationBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationBatch
        fields = ["id", "survey", "created_by", "status", "created_at", "updated_at"]
        read_only_fields = ["created_by", "status", "created_at", "updated_at"]


class BulkInvitationSerializer(serializers.Serializer):
    survey_id = serializers.IntegerField()
    emails = serializers.ListField(child=serializers.EmailField())

    def validate_survey_id(self, value):
        from apps.surveys.models import Survey

        if not Survey.objects.filter(id=value).exists():
            raise serializers.ValidationError("Survey does not exist.")
        return value
