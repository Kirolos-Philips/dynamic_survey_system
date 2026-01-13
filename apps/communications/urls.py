from django.urls import path

from .views import BatchStatusView, BulkInvitationView, InvitationRedeemView

app_name = "communications"

urlpatterns = [
    path("bulk-invite/", BulkInvitationView.as_view(), name="bulk-invite"),
    path(
        "batch-status/<int:batch_id>/", BatchStatusView.as_view(), name="batch-status"
    ),
    path(
        "redeem/<uuid:token>/", InvitationRedeemView.as_view(), name="redeem-invitation"
    ),
]
