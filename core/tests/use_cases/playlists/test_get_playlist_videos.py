from django.contrib.auth.models import AnonymousUser

import pytest

from core.apps.channels.models import Channel
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.exceptions.playlists import (
    PlaylistNotFoundError,
    PlaylistPermissionError,
)
from core.apps.videos.models import Playlist
from core.apps.videos.use_cases.playlists.playlist_videos import GetPlaylistVideosUseCase
from core.tests.factories.videos import (
    PlaylistModelFactory,
    VideoModelFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize('expected_videos', [0, 5, 12, 16, 20, 23])
def test_playlist_videos_retrieved(
    playlist_videos_use_case: GetPlaylistVideosUseCase,
    channel: Channel,
    expected_videos: int,
):
    """Test that videos were retrived successfully."""
    videos = VideoModelFactory.create_batch(size=expected_videos)
    playlist = PlaylistModelFactory.create(status=Playlist.StatusChoices.PUBLIC)
    playlist.videos.set(videos)

    result = playlist_videos_use_case.execute(
        playlist_id=playlist.pk,
        user=user_to_entity(channel.user),
    )

    assert result.count() == playlist.videos.all().count()


@pytest.mark.django_db
def test_playlist_not_exists_error(
    playlist_videos_use_case: GetPlaylistVideosUseCase,
    channel: Channel,
):
    """Test that PlaylistNotFoundError exception has been raised."""

    with pytest.raises(PlaylistNotFoundError):
        playlist_videos_use_case.execute(
            playlist_id='test_playlist_id',
            user=user_to_entity(channel.user),
        )


@pytest.mark.django_db
def test_playlist_permission_error(
    playlist_videos_use_case: GetPlaylistVideosUseCase,
    channel: Channel,
):
    """Test that user can't access and load videos from PRIVATE playlist if he
    is not the author of that playlist."""

    playlist = PlaylistModelFactory.create(status=Playlist.StatusChoices.PRIVATE)

    with pytest.raises(PlaylistPermissionError):
        playlist_videos_use_case.execute(
            playlist_id=playlist.pk,
            user=user_to_entity(channel.user),
        )


@pytest.mark.django_db
def test_playlist_anonymous_permission_error(
    playlist_videos_use_case: GetPlaylistVideosUseCase,
):
    """Test that user can't access and load videos from PRIVATE playlist if he
    is anonymous."""

    playlist = PlaylistModelFactory.create(status=Playlist.StatusChoices.PRIVATE)

    with pytest.raises(PlaylistPermissionError):
        playlist_videos_use_case.execute(
            playlist_id=playlist.pk,
            user=user_to_entity(AnonymousUser()),
        )
