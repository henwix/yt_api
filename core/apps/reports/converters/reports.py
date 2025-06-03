from core.apps.reports.entities.reports import VideoReportEntity
from core.apps.reports.models import VideoReport


def report_from_entity(report: VideoReportEntity) -> VideoReport:
    return VideoReport(
        pk=report.id,
        video_id=report.video_id,
        author_id=report.author_id,
        reason=report.reason,
        description=report.description,
        created_at=report.created_at,
    )


def report_to_entity(report: VideoReport) -> VideoReportEntity:
    return VideoReportEntity(
        id=report.pk,
        video_id=report.video_id,
        author_id=report.author_id,
        reason=report.reason,
        description=report.description,
        created_at=report.created_at,
    )
