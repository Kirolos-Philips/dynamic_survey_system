from django.urls import path

from .views import SurveyDataAPIView, SurveyRenderView

app_name = "surveys"

urlpatterns = [
    path("<int:id>/data/", SurveyDataAPIView.as_view(), name="survey-data"),
    path("<int:id>/", SurveyRenderView.as_view(), name="survey-render"),
]
