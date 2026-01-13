import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.surveys.models import Survey


class InvitationBatch(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="invitation_batches"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_batches",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Invitation Batch")
        verbose_name_plural = _("Invitation Batches")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Batch for {self.survey.title} ({self.created_at})"


class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")
        CLICKED = "clicked", _("Clicked")

    batch = models.ForeignKey(
        InvitationBatch, on_delete=models.CASCADE, related_name="invitations"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_invitations",
    )
    email = models.EmailField(_("Email address"))
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Invitation")
        verbose_name_plural = _("Invitations")
        unique_together = ("batch", "email")

    def __str__(self):
        return f"Invitation for {self.email} to {self.batch.survey.title}"
