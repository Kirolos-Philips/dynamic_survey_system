from rest_framework import permissions

from apps.users.models import User


class IsSurveyManager(permissions.BasePermission):
    """Allows access only to Survey Managers."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.SURVEY_MANAGER
        )


class IsAnalyst(permissions.BasePermission):
    """Allows access only to Analysts."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ANALYST
        )


class IsParticipant(permissions.BasePermission):
    """Allows access only to Participants."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.PARTICIPANT
        )
