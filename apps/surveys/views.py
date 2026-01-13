from django.views.generic import TemplateView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.throttling import ActionBasedThrottle
from apps.surveys.permissions import SurveyPermission
from apps.surveys.serializers import SurveyRenderSerializer
from apps.users.permissions import IsAnalyst, IsParticipant, IsSurveyManager

from .models import Survey


@extend_schema(
    summary="Retrieve Survey Data",
    description=(
        "Fetch a survey by its ID. Data is served from cache for high performance."
    ),
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="The unique ID of the survey",
        ),
    ],
    responses={200: SurveyRenderSerializer},
)
class SurveyDataAPIView(APIView):
    """
    API view to return the survey in a flat schema for specialized frontend rendering.
    """

    permission_classes = [IsSurveyManager | IsAnalyst | IsParticipant, SurveyPermission]
    throttle_classes = [ActionBasedThrottle]
    throttle_map = {
        "get": "survey_view",
    }

    def get(self, request, *args, **kwargs):
        return Response(Survey.get_cached_schema(self.kwargs["id"]))


class SurveyRenderView(TemplateView):
    """
    Template view to render the survey and consume the API.
    """

    template_name = "surveys/survey_render.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["survey_id"] = self.kwargs.get("id")
        return context


class SurveyListView(TemplateView):
    """
    Template view to list available surveys.
    """

    template_name = "surveys/survey_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["surveys"] = Survey.objects.all()
        return context
