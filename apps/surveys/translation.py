from modeltranslation.translator import TranslationOptions, register

from .models import Question, Section, Survey


@register(Survey)
class SurveyTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(Section)
class SectionTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ("text",)
