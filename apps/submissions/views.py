from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.core.throttling import ActionBasedThrottle
from apps.submissions.services import SubmissionValidatorService
from apps.surveys.models import Survey
from apps.users.permissions import (
    IsAnalyst,
    IsParticipant,
    IsSurveyManager,
)

from .models import Submission
from .permissions import SubmissionPermission
from .serializers import SubmissionSerializer


class SubmissionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Submission.objects.all().prefetch_related("answers")
    serializer_class = SubmissionSerializer
    throttle_classes = [ActionBasedThrottle]
    throttle_action_scopes = {
        "create": "submission_create",
        "update": "submission_update",
        "partial_update": "submission_update",
        "retrieve": "slow_get",
    }
    permission_classes = [
        IsSurveyManager | IsAnalyst | IsParticipant,
        SubmissionPermission,
    ]

    def _process_answers(self, submission_serializer: SubmissionSerializer):
        submission = submission_serializer.instance
        status = submission_serializer.validated_data.get(
            "status", Submission.Status.IN_PROGRESS
        )

        # Get all existing answers to be cumulative in validation
        new_answers = submission_serializer.validated_data.get("answers", [])
        if new_answers:
            old_answers = submission.answers.all()
            merged_answers = {str(a.question_id): a.value for a in old_answers}
            for a in new_answers:
                merged_answers[str(a["question"].id)] = a["value"]

            # Validate answers
            SubmissionValidatorService(
                survey_data=Survey.get_cached_schema(submission.survey_id),
                answers_map=merged_answers,
                is_completed=status == Submission.Status.COMPLETED,
            ).validate()

        # SAVE THE ANSWERS TO THE DB
        submission_serializer.save()

        return submission_serializer.data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # IMPORTANT NOTE: THIS INITIAL SAVE DOESN'T COMMIT THE ANSWERS TO THE DB
        serializer.save()
        response_data = self._process_answers(submission_serializer=serializer)
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        submission = self.get_object()
        serializer = self.get_serializer(
            instance=submission, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        # IMPORTANT NOTE: YOU SHOULD NOT SAVE THE SERIALIZER HERE
        response_data = self._process_answers(submission_serializer=serializer)
        return Response(response_data, status=status.HTTP_200_OK)
