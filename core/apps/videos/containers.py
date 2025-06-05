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
from core.apps.videos.services.s3_videos import (
    BaseVideoFilenameValidatorService,
    ComposedVideoFilenameValidatorService,
    VideoFilenameExistsValidatorService,
    VideoFilenameFormatValidatorService,
)
from core.apps.videos.services.videos import (
    BasePrivateVideoPermissionValidatorService,
    BaseVideoAuthorValidatorService,
    BaseVideoHistoryService,
    BaseVideoPlaylistService,
    BaseVideoPrivateOrUploadingValidatorService,
    BaseVideoService,
    BaseVideoValidatorService,
    ORMVideoHistoryService,
    ORMVideoPlaylistService,
    ORMVideoService,
    VideoExistsValidatorService,
    VideoMatchAuthorValidatorService,
    VideoPrivateOrUploadingValidatorService,
    VideoPrivatePermissionValidatorService,
)
from core.apps.videos.use_cases.comments.like_create import CommentLikeCreateUseCase
from core.apps.videos.use_cases.comments.like_delete import CommentLikeDeleteUseCase
from core.apps.videos.use_cases.videos_upload.abort_upload_video import AbortVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.complete_upload_video import CompleteVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.create_upload_video import CreateVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.download_video_url import GenerateUrlForVideoDownloadUseCase
from core.apps.videos.use_cases.videos_upload.upload_video_url import GenerateUrlForVideoUploadUseCase


def init_videos(container: punq.Container) -> None:
    def build_video_filename_validators() -> BaseVideoFilenameValidatorService:
        return ComposedVideoFilenameValidatorService(
            validators=[
                container.resolve(VideoFilenameExistsValidatorService),
                container.resolve(VideoFilenameFormatValidatorService),
            ],
        )

    # init repositories
    container.register(BaseVideoRepository, ORMVideoRepository)
    container.register(BaseVideoHistoryRepository, ORMVideoHistoryRepository)
    container.register(BasePlaylistRepository, ORMPlaylistRepository)
    container.register(BaseVideoCommentRepository, ORMVideoCommentRepository)

    # init services
    container.register(BaseVideoService, ORMVideoService)
    container.register(BaseVideoPlaylistService, ORMVideoPlaylistService)
    container.register(BaseVideoHistoryService, ORMVideoHistoryService)
    container.register(BaseCommentService, ORMCommentService)

    container.register(BaseVideoValidatorService, VideoExistsValidatorService)
    container.register(VideoFilenameExistsValidatorService)
    container.register(VideoFilenameFormatValidatorService)
    container.register(BaseVideoFilenameValidatorService, factory=build_video_filename_validators)
    container.register(BaseVideoAuthorValidatorService, VideoMatchAuthorValidatorService)
    container.register(BasePrivateVideoPermissionValidatorService, VideoPrivatePermissionValidatorService)
    container.register(BaseVideoPrivateOrUploadingValidatorService, VideoPrivateOrUploadingValidatorService)

    # init use cases
    container.register(CommentLikeCreateUseCase)
    container.register(CommentLikeDeleteUseCase)

    container.register(CreateVideoMultipartUploadUseCase)
    container.register(AbortVideoMultipartUploadUseCase)
    container.register(CompleteVideoMultipartUploadUseCase)
    container.register(GenerateUrlForVideoUploadUseCase)
    container.register(GenerateUrlForVideoDownloadUseCase)
