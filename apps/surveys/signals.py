from django.db.models.query_utils import Q
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import Question, QuestionChoice, QuestionLogic, Section, Survey


@receiver([post_save, post_delete], sender=Survey)
def survey_changed(sender, instance: Survey, **kwargs):
    survey = Survey.objects.filter(id=instance.id).last()
    survey.update_schema_cache()


@receiver([post_save, post_delete], sender=Section)
def section_changed(sender, instance: Section, **kwargs):
    survey = Survey.objects.filter(sections=instance.id).last()
    survey.update_schema_cache()


@receiver([post_save, post_delete], sender=Question)
def question_changed(sender, instance: Question, **kwargs):
    survey = Survey.objects.filter(sections__questions=instance.id).last()
    survey.update_schema_cache()


@receiver([post_save, post_delete], sender=QuestionChoice)
def choice_changed(sender, instance: QuestionChoice, **kwargs):
    survey = Survey.objects.filter(
        Q(sections__questions__logic_triggers=instance.id)
        | Q(sections__questions__logic_targets=instance.id)
    )
    survey.update_schema_cache()


@receiver([post_save, post_delete], sender=QuestionLogic)
@receiver(m2m_changed, sender=QuestionLogic.target_choices.through)
def logic_m2m_changed(sender, instance: QuestionLogic, action, **kwargs):
    survey = Survey.objects.filter(
        Q(sections__questions__logic_triggers=instance.id)
        | Q(sections__questions__logic_targets=instance.id)
    ).last()
    survey.update_schema_cache()
