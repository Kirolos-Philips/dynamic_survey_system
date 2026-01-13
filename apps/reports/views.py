from rest_framework import mixins, viewsets

from apps.users.permissions import IsAnalyst, IsSurveyManager

from .models import ReportExport
from .serializers import ReportExportSerializer
from .tasks import generate_survey_report_csv


class ReportExportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ReportExport.objects.all()
    serializer_class = ReportExportSerializer
    permission_classes = [IsSurveyManager | IsAnalyst]

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        export = serializer.save(created_by=self.request.user)
        generate_survey_report_csv.delay(export.id)
