from modeltranslation.translator import TranslationOptions, register

from .models import Question, QuestionChoice, Section, Survey


@register(Survey)
class SurveyTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(Section)
class SectionTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ("text",)


@register(QuestionChoice)
class QuestionChoiceTranslationOptions(TranslationOptions):
    fields = ("label",)
