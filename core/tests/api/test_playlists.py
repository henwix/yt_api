from rest_framework.test import APIClient

import pytest

from core.apps.videos.models import (
    Playlist,
    PlaylistItem,
)
from core.tests.factories.videos import (
    PlaylistItemModelFactory,
    PlaylistModelFactory,
    VideoModelFactory,
)


@pytest.mark.django_db
def test_playlist_created(client: APIClient, jwt_and_channel: str):
    """Test that playlist was created after POST request to the endpoint: /v1/playlists/."""
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)

    assert not Playlist.objects.filter(channel=channel).exists()

    payload = {
        'title': 'Test playlist title',
        'description': 'Test playlist description',
    }

    client.post('v1/playlists/', payload)

    assert not Playlist.objects.filter(channel=channel).exists()


@pytest.mark.django_db
def test_playlist_deleted(client: APIClient, jwt_and_channel: str):
    """Test that playlist was deleted after DELETE request to the endpoint: /v1/playlists/{id}/."""
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    playlist = PlaylistModelFactory.create(channel=channel)

    assert Playlist.objects.filter(channel=channel).exists()

    response = client.delete(f'/v1/playlists/{playlist.id}/')

    assert response.status_code == 204
    assert not Playlist.objects.filter(channel=channel).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('expected_playlists', [2, 5])
def test_playlists_retrieved(client: APIClient, jwt_and_channel: str, expected_playlists: int):
    """Test that playlists were retrieved after GET request to the endpoint: /v1/playlists/."""
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    PlaylistModelFactory.create_batch(size=expected_playlists, channel=channel)

    response = client.get('/v1/playlists/')

    assert response.status_code == 200
    assert len(response.data.get('results')) == expected_playlists


@pytest.mark.django_db
def test_playlists_updated(client: APIClient, jwt_and_channel: str):
    """Test that playlist was updated after PATCH request to the endpoint: /v1/playlists/{id}/."""
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    playlist = PlaylistModelFactory.create(channel=channel)

    payload = {
        'title': 'Test playlist title',
        'description': 'Test playlist description',
    }

    response = client.patch(f'/v1/playlists/{playlist.id}/', payload)

    assert response.status_code == 200
    assert response.data.get('title') == payload.get('title')
    assert response.data.get('description') == payload.get('description')


@pytest.mark.django_db
def test_video_added_to_playlist(client: APIClient, jwt_and_channel: str):
    """Test that video was added to playlist after POST request to the endpoint: /v1/playlists/{id}/add-video/"""
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    video = VideoModelFactory.create(author=channel)
    playlist = PlaylistModelFactory.create(channel=channel)

    assert not PlaylistItem.objects.filter(playlist=playlist, video=video).exists()

    response = client.post(f'/v1/playlists/{playlist.id}/add-video/?v={video.video_id}')

    assert response.status_code == 201
    assert PlaylistItem.objects.filter(playlist=playlist, video=video).exists()


@pytest.mark.django_db
def test_video_add_to_playlist_permission_error(client: APIClient, jwt_and_channel: str):
    """Test that an permission error was returned after POST request to the endpoint: /v1/playlists/{id}/add-video/"""
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    video = VideoModelFactory.create(author=channel)
    other_playlist = PlaylistModelFactory.create()

    assert not PlaylistItem.objects.filter(playlist=other_playlist, video=video).exists()

    response = client.post(f'/v1/playlists/{other_playlist.id}/add-video/?v={video.video_id}')

    assert response.status_code == 403
    assert not PlaylistItem.objects.filter(playlist=other_playlist, video=video).exists()


@pytest.mark.django_db
def test_video_deleted_from_playlist(client: APIClient, jwt_and_channel: str):
    """
    Test that video was deleted from playlist after DELETE request to the endpoint: /v1/playlists/{id}/delete-video/
    """
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    video = VideoModelFactory.create(author=channel)
    other_playlist = PlaylistModelFactory.create()

    PlaylistItemModelFactory(playlist=other_playlist, video=video)

    assert PlaylistItem.objects.filter(playlist=other_playlist, video=video).exists()

    response = client.delete(f'/v1/playlists/{other_playlist.id}/delete-video/?v={video.video_id}')

    assert response.status_code == 403
    assert PlaylistItem.objects.filter(playlist=other_playlist, video=video).exists()
