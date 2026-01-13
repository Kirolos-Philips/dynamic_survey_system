import logging

from django.core.files.base import ContentFile
from django.utils.timezone import now

from apps.reports.models import ReportExport
from apps.submissions.models import Submission
from config.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3)
def generate_survey_report_csv(self, export_id):
    try:
        from apps.submissions.resources import SubmissionResource

        export = ReportExport.objects.get(id=export_id)
        export.status = ReportExport.Status.PROCESSING
        export.save()

        survey = export.survey

        # Initialize resource with survey context
        resource = SubmissionResource(survey=survey)

        # Get queryset with prefetched answers for efficiency
        queryset = Submission.objects.filter(survey=survey).prefetch_related(
            "answers", "user"
        )

        # Use tablib to export
        dataset = resource.export(queryset)
        csv_data = dataset.csv

        # Save to file field
        content_file = ContentFile(csv_data.encode("utf-8-sig"))
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
