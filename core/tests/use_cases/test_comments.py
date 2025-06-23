import punq
import pytest

from core.apps.channels.models import Channel
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.converters.videos import video_to_entity
from core.apps.videos.exceptions.videos import PrivateVideoOrUploadingError
from core.apps.videos.models import Video
from core.apps.videos.use_cases.comments.comment_create import CreateVideoCommentUseCase
from core.tests.factories.videos import VideoModelFactory


@pytest.mark.django_db
def test_comment_creation_use_case_exception(channel: Channel, container: punq.Container):
    """Test that exceptions are raised."""

    use_case: CreateVideoCommentUseCase = container.resolve(CreateVideoCommentUseCase)

    video_uploading = VideoModelFactory.create(upload_status=Video.UploadStatus.UPLOADING)
    video_private = VideoModelFactory.create(status=Video.VideoStatus.PRIVATE)

    #  Test if the video is 'UPLOADING'
    with pytest.raises(PrivateVideoOrUploadingError):
        use_case.execute(
            user=user_to_entity(channel.user),
            video=video_to_entity(video_uploading),
            text='test',
            reply_comment_id=None,
        )

    #  Test if the video is 'PRIVATE'
    with pytest.raises(PrivateVideoOrUploadingError):
        use_case.execute(
            user=user_to_entity(channel.user),
            video=video_to_entity(video_private),
            text='test',
            reply_comment_id=None,
        )
