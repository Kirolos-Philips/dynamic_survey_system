from django.urls import path

from .views import SurveyDataAPIView, SurveyListView, SurveyRenderView

app_name = "surveys"

urlpatterns = [
    path("list/", SurveyListView.as_view(), name="survey-list"),
    path("<int:id>/data/", SurveyDataAPIView.as_view(), name="survey-data"),
    path("<int:id>/", SurveyRenderView.as_view(), name="survey-render"),
]
