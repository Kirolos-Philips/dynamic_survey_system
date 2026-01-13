import csv
import io
import logging

from django.core.files.base import ContentFile
from django.utils.timezone import now

from apps.reports.models import ReportExport
from apps.submissions.models import Submission
from apps.surveys.models import Question
from config.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3)
def generate_survey_report_csv(self, export_id):
    try:
        export = ReportExport.objects.get(id=export_id)
        export.status = ReportExport.Status.PROCESSING
        export.save()

        survey = export.survey
        questions = Question.objects.filter(section__survey=survey).order_by(
            "section__order", "order"
        )
        question_ids = [q.id for q in questions]

        # Headers
        headers = [
            "Submission ID",
            "User",
            "Status",
            "Started At",
            "Completed At",
            "Progress",
        ]
        headers.extend([f"Q: {q.text} ({q.identifier or q.id})" for q in questions])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)

        submissions = Submission.objects.filter(survey=survey).prefetch_related(
            "answers"
        )

        for sub in submissions:
            row = [
                sub.id,
                sub.user.username if sub.user else "Anonymous",
                sub.status,
                sub.started_at.strftime("%Y-%m-%d %H:%M:%S") if sub.started_at else "",
                (
                    sub.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                    if sub.completed_at
                    else ""
                ),
                f"{sub.progress}%",
            ]

            # Map answers by question ID for efficient lookup per row
            answers_map = {ans.question_id: ans.value for ans in sub.answers.all()}

            for q_id in question_ids:
                val = answers_map.get(q_id, "")
                # Format value if it's a list (e.g. checkbox)
                if isinstance(val, list):
                    val = ", ".join(map(str, val))
                row.append(val)

            writer.writerow(row)

        # Save to file field
        content_file = ContentFile(output.getvalue().encode("utf-8-sig"))
        filename = f"report_{survey.id}_{now().strftime('%Y%m%d_%H%M%S')}.csv"
        export.file.save(filename, content_file, save=False)

        export.status = ReportExport.Status.COMPLETED
        export.completed_at = now()
        export.save()

    except ReportExport.DoesNotExist:
        logger.error(f"ReportExport {export_id} does not exist")
    except Exception as e:
        logger.error(f"Error generating report {export_id}: {e}")
        if export:
            export.status = ReportExport.Status.FAILED
            export.error_message = str(e)
            export.save()
        raise self.retry(exc=e) from e
