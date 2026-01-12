from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Answer, Submission


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["question", "value"]

    def validate(self, attrs):
        request_kwargs = self.context["request"].parser_context.get("kwargs", {})
        attrs["submission"] = get_object_or_404(Submission, pk=request_kwargs.get("pk"))
        return attrs

    def create(self, validated_data):
        return Answer.objects.update_or_create(**validated_data)[0]


class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    answers = AnswerSerializer(many=True, required=False)

    class Meta:
        model = Submission
        fields = [
            "id",
            "survey",
            "user",
            "status",
            "progress",
            "answers",
        ]
        read_only_fields = fields

    def create_answer(self, validated_data: dict):
        validated_data.pop("answers", [])
        return super().create(validated_data)
