import pytest

from core.apps.channels.models import Channel
from core.apps.reports.exceptions.reports import ReportLimitError
from core.apps.reports.models import VideoReport
from core.apps.reports.services.reports import BaseVideoReportsService
from core.apps.videos.models import Video
from core.tests.factories.reports import VideoReportModelFactory


@pytest.mark.django_db
def test_get_reports_list_empty(report_service: BaseVideoReportsService):
    """Test report count zero with no products in database."""
    qs = report_service.get_report_list()
    assert qs.count() == 0


@pytest.mark.django_db
def test_get_reports_list_exists(report_service: BaseVideoReportsService):
    """Test all reports retrieved from database."""
    expected_value = 5
    VideoReportModelFactory.create_batch(size=expected_value)

    qs = report_service.get_report_list()
    assert qs.count() == expected_value


@pytest.mark.django_db
def test_reports_created(report_service: BaseVideoReportsService, video: Video, channel: Channel):
    """Test created report exists in database."""
    assert not VideoReport.objects.filter(video=video, author=channel).exists()

    report_service.create_report(
        video_id=video.video_id, user=channel.user, reason='MISINFORMATION', description='Test report description',
    )

    assert VideoReport.objects.filter(video=video, author=channel).exists()


@pytest.mark.django_db
def test_reports_limit_error(report_service: BaseVideoReportsService, video: Video, channel: Channel):
    """Test ReportLimitError when user have reached the limit of reports."""
    VideoReportModelFactory.create_batch(
        size=3,
        video=video,
        author=channel,
    )
    with pytest.raises(ReportLimitError):
        report_service.create_report(
            video_id=video.video_id,
            user=channel.user,
            reason='MISINFORMATION',
            description='Test report description',
        )
