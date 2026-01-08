from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        from django.contrib import admin

        admin.site.site_header = _("Dynamic Survey System Admin")
        admin.site.site_title = _("Survey Admin Portal")
        admin.site.index_title = _("Welcome to the Dynamic Survey Management System")
