from django.contrib import admin
from modeltranslation.admin import (
    TranslationAdmin,
    TranslationStackedInline,
    TranslationTabularInline,
)

from apps.core.admin_mixins import AuditlogHistoryMixin

from .models import Question, QuestionChoice, QuestionLogic, Section, Survey


class QuestionChoiceInline(TranslationTabularInline):
    model = QuestionChoice
    extra = 1


class SectionInline(TranslationStackedInline):
    model = Section
    extra = 1


@admin.register(Survey)
class SurveyAdmin(AuditlogHistoryMixin, TranslationAdmin):
    list_display = ("id", "title", "created_by", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")
    inlines = [SectionInline]


class QuestionInline(TranslationStackedInline):
    model = Question
    extra = 1


@admin.register(Section)
class SectionAdmin(AuditlogHistoryMixin, TranslationAdmin):
    list_display = ("id", "title", "survey", "order")
    list_filter = ("survey",)
    search_fields = ("title", "description")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(AuditlogHistoryMixin, TranslationAdmin):
    list_display = ("id", "text", "section", "question_type", "required", "order")
    list_filter = ("question_type", "required", "section__survey")
    search_fields = ("text",)
    inlines = [QuestionChoiceInline]


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "value", "question", "order")
    list_filter = ("question__section__survey",)
    search_fields = ("label", "value", "question__text")


@admin.register(QuestionLogic)
class QuestionLogicAdmin(AuditlogHistoryMixin, admin.ModelAdmin):
    list_display = ("id", "trigger_question", "target_question", "operator", "action")
    list_filter = ("operator", "action", "trigger_question__section__survey")
    filter_horizontal = ("target_choices",)
    search_fields = ("trigger_question__text", "target_question__text")
