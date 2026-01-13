from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ReportExportViewSet

router = SimpleRouter()
router.register(r"exports", ReportExportViewSet, basename="export")

app_name = "reports"

urlpatterns = [
    path("", include(router.urls)),
]
