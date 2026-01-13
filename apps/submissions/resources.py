from import_export import fields, resources

from apps.submissions.models import Submission
from apps.surveys.models import Question


class SubmissionResource(resources.ModelResource):
    submission_id = fields.Field(attribute="id", column_name="Submission ID")
    username = fields.Field(column_name="User")
    status_display = fields.Field(attribute="get_status_display", column_name="Status")
    started_at = fields.Field(attribute="started_at", column_name="Started At")
    completed_at = fields.Field(attribute="completed_at", column_name="Completed At")
    progress_display = fields.Field(column_name="Progress")

    class Meta:
        model = Submission
        fields = (
            "submission_id",
            "username",
            "status_display",
            "started_at",
            "completed_at",
            "progress_display",
        )
        export_order = fields

    def __init__(self, **kwargs):
        super().__init__()
        self.survey = kwargs.get("survey")
        self.questions = []
        if self.survey:
            # Load questions once during initialization
            self.questions = list(
                Question.objects.filter(section__survey=self.survey).order_by(
                    "section__order", "order"
                )
            )

    def get_queryset(self):
        qs = super().get_queryset().select_related("user")
        return qs.prefetch_related("answers")

    def get_export_fields(self, selected_fields=None):
        fields_list = super().get_export_fields(selected_fields=selected_fields)
        for q in self.questions:
            attr_name = f"question_{q.id}"
            column_name = f"Q: {q.text} ({q.identifier or q.id})"
            # We don't need to specify attribute here if we handle it in export_field
            fields_list.append(
                fields.Field(column_name=column_name, attribute=attr_name)
            )
        return fields_list

    def dehydrate_username(self, submission):
        return submission.user.username if submission.user else "Anonymous"

    def dehydrate_progress_display(self, submission):
        return f"{submission.progress}%"

    def export_field(self, field, obj, **kwargs):
        # Handle dynamic question fields
        if field.attribute and field.attribute.startswith("question_"):
            # Ensure answers are cached for this object to avoid N+1
            if not hasattr(obj, "_answers_map"):
                # Because we used prefetch_related("answers"), this is efficient
                obj._answers_map = {
                    ans.question_id: ans.value for ans in obj.answers.all()
                }

            q_id = int(field.attribute.split("_")[1])
            val = obj._answers_map.get(q_id, "")

            if isinstance(val, list):
                val = ", ".join(map(str, val))
            return val

        return super().export_field(field, obj, **kwargs)
