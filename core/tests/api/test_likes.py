from rest_framework.test import APIClient

import pytest

from core.apps.videos.models import (
    Video,
    VideoLike,
)
from core.tests.factories.videos import VideoLikeModelFactory


@pytest.mark.django_db
def test_video_like_created(client: APIClient, jwt: str, video: Video):
    client.credentials(HTTP_AUTHORIZATION=jwt)

    assert not VideoLike.objects.filter(video=video).exists()

    response = client.post(f'/api/v1/video/{video.video_id}/like/')

    assert response.status_code == 201
    assert VideoLike.objects.filter(video=video).exists()


@pytest.mark.django_db
def test_video_like_deleted(client: APIClient, jwt_and_channel: str, video: Video):
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)

    VideoLikeModelFactory(channel=channel, video=video)

    assert VideoLike.objects.filter(video=video).exists()

    response = client.delete(f'/api/v1/video/{video.video_id}/unlike/')

    assert response.status_code == 204
    assert not VideoLike.objects.filter(video=video).exists()
