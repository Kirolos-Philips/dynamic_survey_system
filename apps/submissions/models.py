from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.surveys.models import Question, Survey


class Submission(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED = "completed", _("Completed")

    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="submissions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_responses",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.IN_PROGRESS
    )
    progress = models.DecimalField(
        _("Progress"), max_digits=5, decimal_places=2, default=0.00
    )
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    if TYPE_CHECKING:
        answers: models.Manager["Answer"]

    class Meta:
        verbose_name = _("Submission")
        verbose_name_plural = _("Submissions")

    def __str__(self):
        return f"Submission for {self.survey.title} by {self.user or 'Anonymous'}"


class Answer(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.JSONField(_("Value"))

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
        unique_together = ("submission", "question")

    def __str__(self):
        return f"Answer to {self.question.identifier or self.question.id}"
