from rest_framework import serializers

from .models import Answer, Submission


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["question", "value"]

    def create(self, validated_data):
        return Answer.objects.update_or_create(
            submission=validated_data["submission"],
            question=validated_data["question"],
            defaults={"value": validated_data["value"]},
        )[0]


class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    answers = AnswerSerializer(many=True, required=False)
    is_completed = serializers.BooleanField(required=False)

    class Meta:
        model = Submission
        fields = [
            "id",
            "survey",
            "user",
            "status",
            "progress",
            "is_completed",
            "answers",
        ]

    read_only_fields = ["id", "survey", "user", "status", "progress"]

    def validate_survey(self, value):
        if self.instance and self.instance.survey != value:
            raise serializers.ValidationError("Survey cannot be changed.")
        return value

    def validate(self, attrs: dict):
        if attrs.pop("is_completed", False):
            attrs["status"] = Submission.Status.COMPLETED
            attrs["progress"] = 100
        return attrs

    def create(self, validated_data):
        answers = validated_data.pop("answers", [])
        submission = Submission.objects.create(**validated_data)
        validated_data["answers"] = answers
        return submission

    def update(self, instance, validated_data):
        answers_data = validated_data.pop("answers", [])

        # Update Submission fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=validated_data.keys())

        # Handle nested answers
        for answer_item in answers_data:
            Answer.objects.update_or_create(
                submission=instance,
                question=answer_item["question"],
                defaults={"value": answer_item["value"]},
            )

        return instance
