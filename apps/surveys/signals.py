from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import Question, QuestionChoice, QuestionLogic, Section, Survey


def invalidate_survey_cache(survey_id):
    if survey_id:
        for lang_code, _ in settings.LANGUAGES:
            cache_key = f"survey_render_{survey_id}_{lang_code}"
            cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Survey)
def survey_changed(sender, instance, **kwargs):
    invalidate_survey_cache(instance.id)


@receiver([post_save, post_delete], sender=Section)
def section_changed(sender, instance, **kwargs):
    invalidate_survey_cache(instance.survey_id)


@receiver([post_save, post_delete], sender=Question)
def question_changed(sender, instance, **kwargs):
    invalidate_survey_cache(instance.section.survey_id)


@receiver([post_save, post_delete], sender=QuestionChoice)
def choice_changed(sender, instance, **kwargs):
    # Some choices might be created without a question initially
    if instance.question_id:
        invalidate_survey_cache(instance.question.section.survey_id)


@receiver([post_save, post_delete], sender=QuestionLogic)
def logic_changed(sender, instance, **kwargs):
    invalidate_survey_cache(instance.trigger_question.section.survey_id)


@receiver(m2m_changed, sender=QuestionLogic.target_choices.through)
def logic_m2m_changed(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        invalidate_survey_cache(instance.trigger_question.section.survey_id)
