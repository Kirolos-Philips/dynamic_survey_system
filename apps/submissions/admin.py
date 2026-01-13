from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export_celery.admin_actions import create_export_job_action

from .models import Answer, Submission
from .resources import SubmissionResource


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ("question", "value")


@admin.register(Submission)
class SubmissionAdmin(ImportExportModelAdmin):
    resource_class = SubmissionResource
    actions = [create_export_job_action]
    list_display = (
        "id",
        "survey",
        "user",
        "status",
        "progress",
        "started_at",
        "completed_at",
    )
    list_filter = ("status", "survey", "started_at")
    search_fields = ("user__username", "survey__title")
    readonly_fields = ("started_at", "updated_at", "completed_at")
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "submission", "question", "value")
    list_filter = ("question__section__survey",)
