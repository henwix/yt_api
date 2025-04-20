import pytest

from core.apps.videos.models import Video
from core.apps.videos.services.comments import BaseCommentService
from core.tests.factories.videos import VideoCommentModelFactory


# TODO: дописать тесты для комментов
@pytest.mark.django_db
def test_comments_retrieved_by_video_id(video: Video, comment_service: BaseCommentService):
    expected_value = 7
    VideoCommentModelFactory.create_batch(
        size=expected_value,
        video=video,
    )
    qs = comment_service.get_comments_by_video_id(video_id=video.video_id)

    assert qs.count() == expected_value
