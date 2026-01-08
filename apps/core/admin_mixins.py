from auditlog.registry import auditlog
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.urls import reverse


class AuditlogHistoryMixin:
    """
    Mixin to redirect the standard Django admin history view to
    the auditlog log entry list for the specific object.

    Only redirects if the model is registered with auditlog.
    """

    def history_view(self, request, object_id, extra_context=None):
        if self.model in auditlog._registry:
            content_type = ContentType.objects.get_for_model(self.model)
            url = (
                reverse("admin:auditlog_logentry_changelist")
                + f"?content_type={content_type.id}&object_pk={object_id}"
            )
            return redirect(url)

        # Fallback to default Django history view if not in auditlog
        return super().history_view(request, object_id, extra_context)
