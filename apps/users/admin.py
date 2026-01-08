from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Participant, SurveyManager, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass


@admin.register(SurveyManager)
class SurveyManagerAdmin(UserAdmin):
    pass


@admin.register(Participant)
class ParticipantAdmin(UserAdmin):
    pass
