import pytest

from core.apps.channels.models import Channel
from core.apps.videos.converters.videos import (
    data_to_video_entity,
    video_from_entity,
)
from core.apps.videos.entities.videos import VideoEntity
from core.apps.videos.exceptions.upload import (
    VideoNotFoundByKeyError,
    VideoNotFoundByUploadIdError,
)
from core.apps.videos.models import Video
from core.apps.videos.services.videos import BaseVideoService
from core.tests.factories.videos import VideoModelFactory


@pytest.mark.django_db
def test_video_created(video_service: BaseVideoService, channel: Channel):
    """Test video created."""
    data = {
        'name': 'Test video',
        'description': 'Test video description',
        'status': Video.VideoStatus.PUBLIC,
        'author_id': channel.pk,
        'upload_id': '123123456456',
    }
    video_service.video_create(data_to_video_entity(data))

    assert Video.objects.filter(
        name='Test video',
        description='Test video description',
        status=Video.VideoStatus.PUBLIC,
        author=channel,
        upload_id='123123456456',
    ).exists()


@pytest.mark.django_db
def test_video_retrieved_by_upload_id(video_service: BaseVideoService):
    """Test video retrieved by upload id."""
    expected_upload_id = '7581294982749kdsjgsd'
    video = VideoModelFactory.create(upload_id=expected_upload_id)

    video_dto = video_from_entity(video_service.get_video_by_upload_id(upload_id=expected_upload_id))
    assert video_dto == video


@pytest.mark.django_db
def test_video_not_found_by_upload_id(video_service: BaseVideoService):
    """Test error raised when video not found by upload id."""
    expected_upload_id = '11hfhgjhtytsdfg'

    with pytest.raises(VideoNotFoundByUploadIdError):
        video_service.get_video_by_upload_id(upload_id=expected_upload_id)


@pytest.mark.django_db
def test_video_retrieved_by_key(video_service: BaseVideoService):
    """Test video retrieved by key."""
    expected_key = 'videos/1lj10nas_test_video.mp4'
    video = VideoModelFactory.create(s3_key=expected_key)

    video_dto = video_from_entity(video_service.get_video_by_key(key=expected_key))

    assert video_dto == video


@pytest.mark.django_db
def test_video_not_found_by_key(video_service: BaseVideoService):
    """Test error raised when video not found by key."""
    expected_key = 'videos/123dsg34_test_video.mp4'

    with pytest.raises(VideoNotFoundByKeyError):
        video_service.get_video_by_key(key=expected_key)


@pytest.mark.django_db
def test_video_updated_after_upload(video_service: BaseVideoService):
    """Test video updated after upload."""
    expected_upload_id = 'kgsfasfbnas'
    expected_s3_key = 'videos/asg3au010124_test_video.mp4'

    # Create Video with 'upload_id' because it's required field to find it in 'update_video_after_upload' repo method
    video = VideoModelFactory.create(upload_id=expected_upload_id)

    assert video.upload_id is not None, 'Upload ID is None'
    assert video.s3_key is None, 'S3 key is not None'

    video_service.update_video_after_upload(
        video_id=video.video_id,
        upload_id=expected_upload_id,
        s3_key=expected_s3_key,
    )

    assert Video.objects.filter(
        video_id=video.video_id,
        upload_id=None,
        s3_key=expected_s3_key,
    ).exists(), 'Video was not updated after upload'


@pytest.mark.django_db
def test_video_deleted_by_id(video_service: BaseVideoService):
    """Test video deleted by id."""
    video = VideoModelFactory.create(upload_id='129847aoshfoa')

    assert Video.objects.filter(video_id=video.video_id).exists()

    video_service.delete_video_by_id(video_id=video.video_id)

    assert not Video.objects.filter(video_id=video.video_id).exists()


@pytest.mark.django_db
def test_video_created_from_entity(video_service: BaseVideoService, channel: Channel):
    entity = VideoEntity(
        author_id=channel.pk,
        name='Test video from entity123',
        upload_id='dgsdg',
        status=Video.VideoStatus.PUBLIC,
    )

    video_service.video_create(video_entity=entity)

    assert Video.objects.filter(
        name='Test video from entity123',
        status=Video.VideoStatus.PUBLIC,
        author=channel,
        upload_id='dgsdg',
    ).exists(), 'Video was not created from entity'
