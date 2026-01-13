from auditlog.registry import auditlog
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


@auditlog.register()
class User(AbstractUser):
    """Base user model for the system."""

    class Role(models.TextChoices):
        SURVEY_MANAGER = "SURVEY_MANAGER", _("Survey Manager")
        ANALYST = "ANALYST", _("Analyst")
        PARTICIPANT = "PARTICIPANT", _("Participant")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.role or 'User'})"


@auditlog.register()
class SurveyManager(User):
    """Concrete model for Survey Manager users using MTI."""

    class Meta:
        verbose_name = _("Survey Manager")
        verbose_name_plural = _("Survey Managers")

    def save(self, *args, **kwargs):
        self.role = User.Role.SURVEY_MANAGER
        super().save(*args, **kwargs)


@auditlog.register()
class Analyst(User):
    """Concrete model for Analyst users using MTI."""

    class Meta:
        verbose_name = _("Analyst")
        verbose_name_plural = _("Analysts")

    def save(self, *args, **kwargs):
        self.role = User.Role.ANALYST
        super().save(*args, **kwargs)


@auditlog.register()
class Participant(User):
    """Concrete model for Participant users using MTI."""

    class Meta:
        verbose_name = _("Participant")
        verbose_name_plural = _("Participants")

    def save(self, *args, **kwargs):
        self.role = User.Role.PARTICIPANT
        super().save(*args, **kwargs)
