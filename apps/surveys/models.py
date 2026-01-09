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
    identifier = models.SlugField(
        _("Identifier"),
        max_length=100,
        help_text=_("Unique string to identify the question in logic strings or API."),
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["order"]
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def __str__(self):
        return self.text


class QuestionChoice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="question_choices"
    )
    label = models.CharField(_("Label"), max_length=255, default="")
    value = models.CharField(_("Value"), max_length=255, default="")
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Question Choice")
        verbose_name_plural = _("Question Choices")

    def __str__(self):
        return f"{self.question} - {self.label}"


@auditlog.register()
class QuestionLogic(models.Model):
    class OperatorChoices(models.TextChoices):
        EQUALS = "eq", _("Equals")
        NOT_EQUALS = "neq", _("Not Equals")
        GREATER_THAN = "gt", _("Greater Than")
        LESS_THAN = "lt", _("Less Than")
        CONTAINS = "contains", _("Contains")

    class ActionChoices(models.TextChoices):
        SHOW = "show", _("Show Question")
        HIDE = "hide", _("Hide Question")
        INCLUDE_CHOICES = ("include_choices", _("Include Specific Choices"))
        EXCLUDE_CHOICES = ("exclude_choices", _("Exclude Specific Choices"))

    trigger_question = models.ForeignKey(
        Question,
        related_name="logic_triggers",
        on_delete=models.CASCADE,
    )
    target_question = models.ForeignKey(
        Question,
        related_name="logic_targets",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    operator = models.CharField(max_length=10, choices=OperatorChoices.choices)
    value = models.JSONField(_("Value"))  # Value to compare against

    action = models.CharField(max_length=20, choices=ActionChoices.choices)
    target_choices = models.ManyToManyField(
        QuestionChoice, related_name="question_logics"
    )

    class Meta:
        verbose_name = _("Question Logic")
        verbose_name_plural = _("Question Logics")

    def __str__(self):
        return f"{_('Logic for')} {self.trigger_question}"
