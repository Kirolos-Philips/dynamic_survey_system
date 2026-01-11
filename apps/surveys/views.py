from django.views.generic import TemplateView
from rest_framework import generics

from .models import Survey
from .serializers import SurveyRenderSerializer


class SurveyDataAPIView(generics.RetrieveAPIView):
    """
    API view to return the survey in a flat schema for specialized frontend rendering.
    """

    queryset = Survey.objects.all()
    serializer_class = SurveyRenderSerializer
    lookup_field = "id"


class SurveyRenderView(TemplateView):
    """
    Template view to render the survey and consume the API.
    """

    template_name = "surveys/survey_render.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["survey_id"] = self.kwargs.get("id")
        return context
