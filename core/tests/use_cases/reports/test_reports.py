import pytest

from core.apps.channels.models import Channel
from core.apps.reports.exceptions.reports import ReportLimitError
from core.apps.reports.use_cases.create import CreateReportUseCase
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.models import Video
from core.tests.factories.reports import VideoReportModelFactory


@pytest.mark.django_db
def test_reports_limit_error(create_report_use_case: CreateReportUseCase, video: Video, channel: Channel):
    """Test that an error has been raised when the report limit is exceeded."""

    VideoReportModelFactory.create_batch(
        size=3,
        video=video,
        author=channel,
    )
    with pytest.raises(ReportLimitError):
        create_report_use_case.execute(
            video_id=video.pk,
            user=user_to_entity(channel.user),
            reason='MISINFORMATION',
            description='Test report description',
        )
