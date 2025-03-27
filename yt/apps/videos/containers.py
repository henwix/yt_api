import punq

from apps.videos.repositories.videos import BaseVideoRepository, ORMVideoRepository
from apps.videos.services.videos import BaseVideoService, VideoService


def initialize_videos(container: punq.Container) -> None:
    # repositories
    container.register(BaseVideoRepository, ORMVideoRepository)

    # services
    container.register(BaseVideoService, VideoService)
