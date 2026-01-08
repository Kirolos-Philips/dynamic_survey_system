from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Base user model for the system."""

    def __str__(self):
        return self.username


class SurveyManager(User):
    """Concrete model for Survey Manager users using MTI."""

    class Meta:
        verbose_name = _("Survey Manager")
        verbose_name_plural = _("Survey Managers")


class Participant(User):
    """Concrete model for Participant users using MTI."""

    class Meta:
        verbose_name = _("Participant")
        verbose_name_plural = _("Participants")
