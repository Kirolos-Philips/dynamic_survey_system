from rest_framework import serializers

from .models import Question, QuestionChoice, QuestionLogic, Survey


class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = ["id", "value", "label"]


class QuestionRenderSerializer(serializers.ModelSerializer):
    section = serializers.CharField(source="section.title")
    type = serializers.CharField(source="question_type")
    choices = QuestionChoiceSerializer(many=True, source="question_choices")

    text = serializers.SerializerMethodField()

    def get_text(self, obj: Question):
        return f"{obj.id} - {obj.text}"

    class Meta:
        model = Question
        fields = ["id", "section", "text", "type", "choices"]


class SurveyRenderSerializer(serializers.ModelSerializer):
    questions_map = serializers.SerializerMethodField()
    logic_map = serializers.SerializerMethodField()
    trigger_map = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            "id",
            "title",
            "description",
            "questions_map",
            "logic_map",
            "trigger_map",
        ]

    def get_questions_map(self, obj):
        questions = (
            Question.objects.filter(section__survey=obj)
            .select_related("section")
            .prefetch_related("question_choices")
            .order_by("section", "order")
        )
        return QuestionRenderSerializer(questions, many=True).data

    def get_logic_map(self, obj):
        logics = (
            QuestionLogic.objects.filter(trigger_question__section__survey=obj)
            .select_related("trigger_question", "target_question")
            .prefetch_related("target_choices")
        )

        logic_map = {}
        for logic in logics:
            if not logic.target_question_id:
                continue

            target_id = str(logic.target_question_id)
            if target_id not in logic_map:
                logic_map[target_id] = []

            rule = {
                "trigger_question": logic.trigger_question_id,
                "operator": logic.operator,
                "value": logic.value,
                "action": logic.action,
            }

            if logic.target_choices.exists():
                rule["target_choices"] = list(
                    logic.target_choices.values_list("id", flat=True)
                )

            logic_map[target_id].append(rule)

        return logic_map

    def get_trigger_map(self, obj):
        logics = (
            QuestionLogic.objects.filter(trigger_question__section__survey=obj)
            .values("trigger_question_id", "target_question_id")
            .distinct()
        )

        trigger_map = {}
        for logic in logics:
            if not logic["target_question_id"]:
                continue

            trigger_id = str(logic["trigger_question_id"])
            if trigger_id not in trigger_map:
                trigger_map[trigger_id] = []

            if logic["target_question_id"] not in trigger_map[trigger_id]:
                trigger_map[trigger_id].append(logic["target_question_id"])

        return trigger_map
