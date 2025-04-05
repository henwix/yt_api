import punq

from core.apps.videos.repositories.videos import (
    BasePlaylistRepository,
    BaseVideoHistoryRepository,
    BaseVideoRepository,
    ORMVideoRepository,
    PlaylistRepository,
    VideoHistoryRepository,
)
from core.apps.videos.services.videos import (
    BaseVideoHistoryService,
    BaseVideoPlaylistService,
    BaseVideoPresignedURLService,
    BaseVideoService,
    VideoHistoryService,
    VideoPlaylistService,
    VideoPresignedURLService,
    VideoService,
)


def initialize_videos(container: punq.Container) -> None:
    # repositories
    container.register(BaseVideoRepository, ORMVideoRepository)
    container.register(BaseVideoHistoryRepository, VideoHistoryRepository)
    container.register(BasePlaylistRepository, PlaylistRepository)

    # services
    container.register(BaseVideoService, VideoService)
    container.register(BaseVideoHistoryService, VideoHistoryService)
    container.register(BaseVideoPresignedURLService, VideoPresignedURLService)
    container.register(BaseVideoPlaylistService, VideoPlaylistService)
