from rest_framework import permissions

from apps.submissions.models import Submission


class SubmissionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        return bool(
            user.is_participant
            or user.is_survey_manager
            or user.is_analyst
            or user.is_superuser
        )

    def has_object_permission(self, request, view, obj: Submission):
        return obj.user == request.user
