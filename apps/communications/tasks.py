import logging

from django.utils.timezone import now

from config.celery import app

from .models import Invitation, InvitationBatch

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3)
def send_invitation_batch(self, batch_id):
    try:
        from django.conf import settings
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string

        batch = InvitationBatch.objects.get(id=batch_id)
        batch.status = InvitationBatch.Status.PROCESSING
        batch.save()

        invitations = batch.invitations.filter(status=Invitation.Status.PENDING)

        for invitation in invitations:
            try:
                subject = f"Invitation to participate in {batch.survey.title}"
                action_url = (
                    f"{settings.SITE_URL}/surveys/render/{batch.survey.id}/"
                    f"?token={invitation.token}"
                )

                context = {
                    "survey_title": batch.survey.title,
                    "survey_description": batch.survey.description,
                    "action_url": action_url,
                    "current_year": now().year,
                }

                text_content = render_to_string(
                    "communications/emails/invitation_email.txt", context
                )
                html_content = render_to_string(
                    "communications/emails/invitation_email.html", context
                )

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[invitation.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                invitation.status = Invitation.Status.SENT
                invitation.sent_at = now()
            except Exception as e:
                logger.error(f"Failed to send invitation to {invitation.email}: {e}")
                invitation.status = Invitation.Status.FAILED
                invitation.error_message = str(e)

            invitation.save()

        batch.status = InvitationBatch.Status.COMPLETED
        batch.save()

    except InvitationBatch.DoesNotExist:
        logger.error(f"InvitationBatch {batch_id} does not exist")
    except Exception as e:
        logger.error(f"Error processing batch {batch_id}: {e}")
        if batch:
            batch.status = InvitationBatch.Status.FAILED
            batch.save()
        raise self.retry(exc=e) from e
