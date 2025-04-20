import punq

from core.apps.videos.repositories.comments import (
    BaseVideoCommentRepository,
    ORMVideoCommentRepository,
)
from core.apps.videos.repositories.videos import (
    BasePlaylistRepository,
    BaseVideoHistoryRepository,
    BaseVideoRepository,
    ORMPlaylistRepository,
    ORMVideoHistoryRepository,
    ORMVideoRepository,
)
from core.apps.videos.services.comments import (
    BaseCommentService,
    ORMCommentService,
)
from core.apps.videos.services.videos import (
    BaseVideoHistoryService,
    BaseVideoPlaylistService,
    BaseVideoPresignedURLService,
    BaseVideoService,
    ORMVideoHistoryService,
    ORMVideoPlaylistService,
    ORMVideoPresignedURLService,
    ORMVideoService,
)
from core.apps.videos.use_cases.comments.like_create import LikeCreateUseCase
from core.apps.videos.use_cases.comments.like_delete import LikeDeleteUseCase


def init_videos(container: punq.Container) -> None:
    # repositories
    container.register(BaseVideoRepository, ORMVideoRepository)
    container.register(BaseVideoHistoryRepository, ORMVideoHistoryRepository)
    container.register(BasePlaylistRepository, ORMPlaylistRepository)
    container.register(BaseVideoCommentRepository, ORMVideoCommentRepository)

    # services
    container.register(BaseVideoService, ORMVideoService)
    container.register(BaseVideoHistoryService, ORMVideoHistoryService)
    container.register(BaseVideoPresignedURLService, ORMVideoPresignedURLService)
    container.register(BaseVideoPlaylistService, ORMVideoPlaylistService)
    container.register(BaseCommentService, ORMCommentService)

    # use cases
    container.register(LikeCreateUseCase)
    container.register(LikeDeleteUseCase)
