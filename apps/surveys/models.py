from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


@auditlog.register()
class Survey(models.Model):
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Created by"),
    )
    is_active = models.BooleanField(_("Is active"), default=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")

    def __str__(self):
        return self.title


@auditlog.register()
class Section(models.Model):
    survey = models.ForeignKey(
        Survey,
        related_name="sections",
        on_delete=models.CASCADE,
        verbose_name=_("Survey"),
    )
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    def __str__(self):
        return f"{self.survey.title} - {self.title}"


@auditlog.register()
class Question(models.Model):
    class QuestionType(models.TextChoices):
        TEXT = "text", _("Text")
        NUMBER = "number", _("Number")
        DROPDOWN = "dropdown", _("Dropdown")
        RADIO = "radio", _("Radio Button")
        CHECKBOX = "checkbox", _("Checkbox")
        DATE = "date", _("Date")

    section = models.ForeignKey(
        Section,
        related_name="questions",
        on_delete=models.CASCADE,
        verbose_name=_("Section"),
    )
    text = models.CharField(_("Text"), max_length=500)
    question_type = models.CharField(
        _("Question type"), max_length=20, choices=QuestionType.choices
    )
    required = models.BooleanField(_("Required"), default=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    configuration = models.JSONField(
        _("Configuration"), default=dict, blank=True
    )  # Store options for dropdown/radio etc.

    class Meta:
        ordering = ["order"]
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def __str__(self):
        return self.text


@auditlog.register()
class QuestionLogic(models.Model):
    class OperatorChoices(models.TextChoices):
        EQUALS = "eq", _("Equals")
        NOT_EQUALS = "neq", _("Not Equals")
        GREATER_THAN = "gt", _("Greater Than")
        LESS_THAN = "lt", _("Less Than")
        CONTAINS = "contains", _("Contains")

    ACTION_CHOICES = [
        (True, _("Show")),
        (False, _("Hide")),
    ]

    trigger_question = models.ForeignKey(
        Question,
        related_name="logic_triggers",
        on_delete=models.CASCADE,
        verbose_name=_("Trigger question"),
    )
    target_question = models.ForeignKey(
        Question,
        related_name="logic_targets",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Target question"),
    )
    target_section = models.ForeignKey(
        Section,
        related_name="logic_targets",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Target section"),
    )
    operator = models.CharField(
        _("Operator"), max_length=10, choices=OperatorChoices.choices
    )
    value = models.JSONField(_("Value"))  # Value to compare against

    action = models.BooleanField(_("Action"), choices=ACTION_CHOICES, default=True)

    class Meta:
        verbose_name = _("Question Logic")
        verbose_name_plural = _("Question Logics")

    def __str__(self):
        return f"{_('Logic for')} {self.trigger_question}"
