import punq
import pytest

from core.apps.videos.models import Playlist
from core.apps.videos.use_cases.playlists.playlist_videos import GetPlaylistVideosUseCase
from core.tests.factories.videos import (
    PlaylistModelFactory,
    VideoModelFactory,
)


@pytest.fixture
def playlist_videos_use_case(container: punq.Container) -> GetPlaylistVideosUseCase:
    return container.resolve(GetPlaylistVideosUseCase)


@pytest.fixture
def playlist() -> Playlist:
    videos = VideoModelFactory.create_batch(size=26)

    playlist = PlaylistModelFactory.create(status=Playlist.StatusChoices.PUBLIC)
    playlist.videos.set(videos)

    return playlist
