from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.core.admin_mixins import AuditlogHistoryMixin

from .models import Analyst, Participant, SurveyManager, User


@admin.register(User)
class UserAdmin(AuditlogHistoryMixin, BaseUserAdmin):
    pass


@admin.register(SurveyManager)
class SurveyManagerAdmin(UserAdmin):
    pass


@admin.register(Analyst)
class AnalystAdmin(UserAdmin):
    pass


@admin.register(Participant)
class ParticipantAdmin(UserAdmin):
    pass
