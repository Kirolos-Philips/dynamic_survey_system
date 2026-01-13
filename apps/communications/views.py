from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsSurveyManager

from .models import Invitation, InvitationBatch
from .serializers import BulkInvitationSerializer
from .tasks import send_invitation_batch


class BulkInvitationView(APIView):
    permission_classes = [IsAuthenticated, IsSurveyManager]

    def post(self, request, *args, **kwargs):
        serializer = BulkInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        survey_id = serializer.validated_data["survey_id"]
        emails = serializer.validated_data["emails"]

        batch = InvitationBatch.objects.create(
            survey_id=survey_id,
            created_by=request.user,
            metadata={"total_emails": len(emails)},
        )

        invitations = [Invitation(batch=batch, email=email) for email in emails]
        Invitation.objects.bulk_create(invitations)

        # Trigger Celery task
        send_invitation_batch.delay(batch.id)

        return Response(
            {
                "batch_id": batch.id,
                "message": (
                    f"Successfully queued {len(emails)} invitations for sending."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class BatchStatusView(APIView):
    permission_classes = [IsAuthenticated, IsSurveyManager]

    def get(self, request, batch_id):
        try:
            batch = InvitationBatch.objects.get(id=batch_id)
            return Response(
                {
                    "id": batch.id,
                    "status": batch.status,
                    "total": batch.invitations.count(),
                    "sent": batch.invitations.filter(
                        status=Invitation.Status.SENT
                    ).count(),
                    "failed": batch.invitations.filter(
                        status=Invitation.Status.FAILED
                    ).count(),
                    "pending": batch.invitations.filter(
                        status=Invitation.Status.PENDING
                    ).count(),
                    "created_at": batch.created_at,
                }
            )
        except InvitationBatch.DoesNotExist:
            return Response(
                {"error": "Batch not found"}, status=status.HTTP_404_NOT_FOUND
            )


class InvitationRedeemView(APIView):
    """
    View to redeem an invitation token and redirect or return survey link.
    """

    def get(self, request, token):
        try:
            invitation = Invitation.objects.get(token=token)
            invitation.status = Invitation.Status.CLICKED
            invitation.save()

            # Here we could either redirect or return the survey URL
            # For now, let's return the URL where they can take the survey
            return Response(
                {
                    "survey_id": invitation.batch.survey.id,
                    "survey_title": invitation.batch.survey.title,
                    "invitation_token": str(token),
                    "take_survey_url": (
                        f"/surveys/render/{invitation.batch.survey.id}/?token={token}"
                    ),
                }
            )
        except Invitation.DoesNotExist:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND
            )
