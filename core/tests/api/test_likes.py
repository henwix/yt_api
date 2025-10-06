from rest_framework.test import APIClient

import pytest

from core.apps.videos.models import (
    Video,
    VideoLike,
)
from core.tests.factories.videos import VideoLikeModelFactory


@pytest.mark.django_db
def test_video_like_created(client: APIClient, jwt: str, video: Video):
    """Test that video like was created after POST request to the endpoint: /v1/videos/{video_id}/like/."""

    client.credentials(HTTP_AUTHORIZATION=jwt)

    assert not VideoLike.objects.filter(video=video).exists()

    response = client.post(f'/v1/videos/{video.video_id}/like/')

    assert response.status_code == 201, 'incorrect code'
    assert VideoLike.objects.filter(video=video).exists()


@pytest.mark.django_db
def test_video_like_deleted(client: APIClient, jwt_and_channel: tuple, video: Video):
    """Test that video like was deleted after DELETE request to the endpoint: /v1/videos/{video_id}/unlike/."""

    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)

    VideoLikeModelFactory(channel=channel, video=video)

    assert VideoLike.objects.filter(video=video).exists()

    response = client.delete(f'/v1/videos/{video.video_id}/unlike/')

    assert response.status_code == 200, 'incorrect code'
    assert not VideoLike.objects.filter(video=video).exists()
