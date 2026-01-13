from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.surveys.models import Survey


class ReportExport(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="exports")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    file = models.FileField(upload_to="exports/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Report Export")
        verbose_name_plural = _("Report Exports")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Export for {self.survey.title} - {self.status}"
