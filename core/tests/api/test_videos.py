from rest_framework.test import APIClient

import pytest

from core.apps.videos.models import Video
from core.tests.factories.channels import SubscriptionItemModelFactory
from core.tests.factories.video_comments import VideoCommentModelFactory
from core.tests.factories.videos import (
    VideoLikeModelFactory,
    VideoModelFactory,
    VideoViewModelFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'expected_views, expected_subs, expected_likes, expected_comments', (
        [7, 4, 11, 6], [2, 7, 1, 3], [3, 2, 8, 7], [8, 12, 5, 9],
    ),
)
def test_video_retrieved(
    client: APIClient,
    video: Video,
    expected_views: int,
    expected_subs: int,
    expected_likes: int,
    expected_comments: int,
):
    """Test that video has been retrieved after GET request and response is
    correct."""
    SubscriptionItemModelFactory.create_batch(size=expected_subs, subscribed_to=video.author)
    VideoViewModelFactory.create_batch(size=expected_views, video=video)
    VideoLikeModelFactory.create_batch(size=expected_likes, video=video)
    VideoCommentModelFactory.create_batch(size=expected_comments, video=video)

    url = f'/v1/videos/{video.video_id}/'
    response = client.get(url)

    assert response.status_code == 200
    assert url in response.data.get('video_link')
    assert response.data.get('name') == video.name
    assert response.data.get('description') == video.description
    assert response.data.get('status') == video.status
    assert response.data.get('author_name') == video.author.name
    assert response.data.get('views_count') == expected_views
    assert response.data.get('subs_count') == expected_subs
    assert response.data.get('likes_count') == expected_likes
    assert response.data.get('comments_count') == expected_comments


@pytest.mark.django_db
def test_video_deleted(client: APIClient, jwt_and_channel: tuple):
    """Test that video has been deleted from database after DELETE request."""
    jwt, channel = jwt_and_channel
    video = VideoModelFactory.create(author=channel)
    client.credentials(HTTP_AUTHORIZATION=jwt)

    assert Video.objects.filter(video_id=video.video_id).exists()

    response = client.delete(f'/v1/videos/{video.video_id}/')

    assert response.status_code == 204
    assert not Video.objects.filter(video_id=video.video_id).exists()


@pytest.mark.django_db
def test_video_updated(client: APIClient, jwt_and_channel: tuple):
    """Test that video has been updated after PATCH request."""
    jwt, channel = jwt_and_channel
    video = VideoModelFactory.create(author=channel)
    client.credentials(HTTP_AUTHORIZATION=jwt)

    payload = {
        'name': 'Test video name 123',
        'description': 'Test video description',
        'status': 'PRIVATE',
    }

    response = client.patch(f'/v1/videos/{video.video_id}/', payload)

    assert response.status_code == 200
    assert response.data.get('name') == payload.get('name')
    assert response.data.get('description') == payload.get('description')
    assert response.data.get('status') == payload.get('status')


@pytest.mark.django_db
def test_video_search(client: APIClient):
    """Test that videos were found and retrieved after searching."""
    VideoModelFactory.create(name='test')  # create video with name 'test'
    VideoModelFactory.create(description='test')  # create video with description 'test'

    response = client.get('/v1/videos/?search=test')

    assert response.status_code == 200
    assert len(response.data.get('results')) == 2
