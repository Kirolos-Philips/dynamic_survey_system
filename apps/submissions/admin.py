from django.contrib import admin

from .models import Answer, Submission


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ("question", "value")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
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
