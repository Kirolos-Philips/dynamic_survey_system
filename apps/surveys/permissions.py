from rest_framework import permissions


class SurveyPermission(permissions.BasePermission):
    """
    General Survey Permissions:
    - Managers & Admins: Full Access
    - Analysts: Read-only
    - Participants: Read-only (View templates to take them)
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_survey_manager or user.is_superuser:
            return True

        if user.is_analyst or user.is_participant:
            return request.method in permissions.SAFE_METHODS

        return False
