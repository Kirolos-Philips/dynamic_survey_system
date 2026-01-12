from django.apps import AppConfig


class SurveysConfig(AppConfig):
    name = "apps.surveys"

    def ready(self):
        import apps.surveys.signals  # noqa
