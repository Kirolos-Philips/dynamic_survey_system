from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline

from apps.core.admin_mixins import AuditlogHistoryMixin

from .models import Question, QuestionLogic, Section, Survey


class SectionInline(TranslationStackedInline):
    model = Section
    extra = 1


@admin.register(Survey)
class SurveyAdmin(AuditlogHistoryMixin, TranslationAdmin):
    list_display = ("title", "created_by", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")
    inlines = [SectionInline]


class QuestionInline(TranslationStackedInline):
    model = Question
    extra = 1


@admin.register(Section)
class SectionAdmin(AuditlogHistoryMixin, TranslationAdmin):
    list_display = ("title", "survey", "order")
    list_filter = ("survey",)
    search_fields = ("title", "description")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(AuditlogHistoryMixin, TranslationAdmin):
    list_display = ("text", "section", "question_type", "required", "order")
    list_filter = ("question_type", "required", "section__survey")
    search_fields = ("text",)


@admin.register(QuestionLogic)
class QuestionLogicAdmin(AuditlogHistoryMixin, admin.ModelAdmin):
    list_display = ("trigger_question", "operator", "action")
    list_filter = ("operator", "action")
