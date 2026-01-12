from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.submissions.serializers import AnswerSerializer
from apps.submissions.services import SubmissionValidatorService
from apps.surveys.serializers import SurveyRenderSerializer

from .models import Submission
from .serializers import SubmissionSerializer


class SubmissionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Submission.objects.all().prefetch_related("answers")
    serializer_class = SubmissionSerializer

    def _process_answers(self, answers_list: list[dict], submission: Submission):
        serializer: AnswerSerializer = self.get_serializer(data=answers_list, many=True)
        serializer.is_valid(raise_exception=True)

        survey_data = SurveyRenderSerializer(submission.survey).data
        answers_map = {
            str(answer["question"].id): answer["value"]
            for answer in serializer.validated_data
        }

        SubmissionValidatorService(
            survey_data=survey_data, answers_map=answers_map, is_completed=False
        ).validate()
        serializer.save()

        submission.refresh_from_db()

        updated_submission = self.get_queryset().get(id=submission.id)
        return Response(
            SubmissionSerializer(updated_submission).data,
            status=status.HTTP_200_OK,
            headers=self.get_success_headers(serializer.data),
        )

    def create(self, request, *args, **kwargs):
        serializer: SubmissionSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self._process_answers(
            answers_list=serializer.validated_data.pop("answers", []) or [],
            submission=serializer.instance,
        )

    def update(self, request, *args, **kwargs):
        serializer: SubmissionSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._process_answers(
            answers_list=serializer.validated_data.get("answers", []) or [],
            submission=serializer.instance,
        )
