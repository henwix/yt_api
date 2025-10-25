import pytest
from rest_framework.test import APIClient

from core.apps.videos.exceptions.videos import ViewExistsError
from core.apps.videos.models import (
    Video,
    VideoView,
)
from core.tests.factories.videos import VideoViewModelFactory


@pytest.mark.django_db
def test_video_view_created(client: APIClient, jwt: str, video: Video):
    """Test that video view was created after POST request to the endpoint: /v1/videos/{video_id}/view/."""

    client.credentials(HTTP_AUTHORIZATION=jwt)

    assert not VideoView.objects.filter(video=video).exists()

    response = client.post(f'/v1/videos/{video.video_id}/view/')

    assert response.status_code == 201
    assert VideoView.objects.filter(video=video).exists()


@pytest.mark.django_db
def test_video_view_exists_error(client: APIClient, jwt_and_channel: tuple, video: Video):
    """Test that video view was created after POST request to the endpoint: /v1/videos/{video_id}/view/."""

    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)

    VideoViewModelFactory.create(video=video, channel=channel)

    assert VideoView.objects.filter(video=video, channel=channel).exists()
    assert VideoView.objects.filter(video=video, channel=channel).count() == 1

    response = client.post(f'/v1/videos/{video.video_id}/view/')

    assert response.status_code == ViewExistsError.status_code
    assert response.data.get('detail') == ViewExistsError.default_detail['detail']
    assert VideoView.objects.filter(video=video, channel=channel).count() == 1
