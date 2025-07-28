import pytest

from core.apps.channels.converters.channels import channel_to_entity
from core.apps.channels.models import Channel
from core.apps.reports.models import VideoReport
from core.apps.reports.services.reports import BaseVideoReportsService
from core.apps.videos.converters.videos import video_to_entity
from core.apps.videos.models import Video
from core.tests.factories.reports import VideoReportModelFactory


@pytest.mark.django_db
def test_get_reports_list_empty(report_service: BaseVideoReportsService):
    """Test that the report list is empty and the count equals 0."""

    qs = report_service.get_report_list()
    assert qs.count() == 0


@pytest.mark.django_db
def test_get_reports_list_exists(report_service: BaseVideoReportsService):
    """Test that all reports were retrieved from the database."""

    expected_value = 5
    VideoReportModelFactory.create_batch(size=expected_value)

    qs = report_service.get_report_list()
    assert qs.count() == expected_value


@pytest.mark.django_db
def test_reports_created(report_service: BaseVideoReportsService, video: Video, channel: Channel):
    """Test that created report exists in database."""

    assert not VideoReport.objects.filter(video=video, author=channel).exists()

    report_service.create_report(
        video=video_to_entity(video),
        author=channel_to_entity(channel),
        reason='MISINFORMATION',
        description='Test report description',
    )

    assert VideoReport.objects.filter(video=video, author=channel).exists()
