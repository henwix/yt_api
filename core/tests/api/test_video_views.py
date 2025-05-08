from rest_framework.test import APIClient

import pytest

from core.apps.videos.models import (
    Video,
    VideoView,
)


@pytest.mark.django_db
def test_video_view_created(client: APIClient, jwt: str, video: Video):
    client.credentials(HTTP_AUTHORIZATION=jwt)

    assert not VideoView.objects.filter(video=video).exists()

    response = client.post(f'/api/v1/videos/{video.video_id}/view/')

    assert response.status_code == 201
    assert VideoView.objects.filter(video=video).exists()
