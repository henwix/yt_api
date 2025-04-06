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
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)

    assert not Playlist.objects.filter(channel=channel).exists()

    payload = {
        'title': 'Test playlist title',
        'description': 'Test playlist description',
    }

    client.post('api/v1/playlist/', payload)

    assert not Playlist.objects.filter(channel=channel).exists()


@pytest.mark.django_db
def test_playlist_deleted(client: APIClient, jwt_and_channel: str):
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    playlist = PlaylistModelFactory.create(channel=channel)

    assert Playlist.objects.filter(channel=channel).exists()

    response = client.delete(f'/api/v1/playlist/{playlist.id}/')

    assert response.status_code == 204
    assert not Playlist.objects.filter(channel=channel).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('expected_playlists', [2, 5])
def test_playlists_retrieved(client: APIClient, jwt_and_channel: str, expected_playlists: int):
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    PlaylistModelFactory.create_batch(size=expected_playlists, channel=channel)

    response = client.get('/api/v1/playlist/')

    assert response.status_code == 200
    assert len(response.data.get('results')) == expected_playlists


@pytest.mark.django_db
def test_playlists_updated(client: APIClient, jwt_and_channel: str):
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    playlist = PlaylistModelFactory.create(channel=channel)

    payload = {
        'title': 'Test playlist title',
        'description': 'Test playlist description',
    }

    response = client.patch(f'/api/v1/playlist/{playlist.id}/', payload)

    assert response.status_code == 200
    assert response.data.get('title') == payload.get('title')
    assert response.data.get('description') == payload.get('description')


@pytest.mark.django_db
def test_video_added_to_playlist(client: APIClient, jwt_and_channel: str):
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    video = VideoModelFactory.create(author=channel)
    playlist = PlaylistModelFactory.create(channel=channel)

    assert not PlaylistItem.objects.filter(playlist=playlist, video=video).exists()

    response = client.post(f'/api/v1/playlist/{playlist.id}/add-video/?v={video.video_id}')

    assert response.status_code == 201
    assert PlaylistItem.objects.filter(playlist=playlist, video=video).exists()


@pytest.mark.django_db
def test_video_deleted_from_playlist(client: APIClient, jwt_and_channel: str):
    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)
    video = VideoModelFactory.create(author=channel)
    playlist = PlaylistModelFactory.create(channel=channel)

    PlaylistItemModelFactory(playlist=playlist, video=video)

    assert PlaylistItem.objects.filter(playlist=playlist, video=video).exists()

    response = client.delete(f'/api/v1/playlist/{playlist.id}/delete-video/?v={video.video_id}')

    assert response.status_code == 204
    assert not PlaylistItem.objects.filter(playlist=playlist, video=video).exists()
