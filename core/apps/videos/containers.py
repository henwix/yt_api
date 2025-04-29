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
from core.apps.videos.services.upload import (
    BaseFilenameValidatorService,
    BaseVideoS3UploadValidatorService,
    ComposedFilenameValidatorService,
    FilenameExistsValidatorService,
    FilenameFormatValidatorService,
    VideoS3UploadExistsValidatorService,
)
from core.apps.videos.services.videos import (
    BaseS3VideoService,
    BaseVideoHistoryService,
    BaseVideoPlaylistService,
    BaseVideoPresignedURLService,
    BaseVideoService,
    BaseVideoValidatorService,
    ORMVideoHistoryService,
    ORMVideoPlaylistService,
    ORMVideoPresignedURLService,
    ORMVideoService,
    S3VideoService,
    VideoExistsValidatorService,
)
from core.apps.videos.use_cases.comments.like_create import LikeCreateUseCase
from core.apps.videos.use_cases.comments.like_delete import LikeDeleteUseCase
from core.apps.videos.use_cases.multipart_upload.abort_upload import AbortMultipartUploadUseCase
from core.apps.videos.use_cases.multipart_upload.complete_upload import CompleteUploadUseCase
from core.apps.videos.use_cases.multipart_upload.initiate_upload import InitiateMultipartUploadUseCase
from core.apps.videos.use_cases.multipart_upload.presigned_url_upload import GenerateUrlForUploadUseCase


def init_videos(container: punq.Container) -> None:
    def build_filename_validators() -> BaseFilenameValidatorService:
        return ComposedFilenameValidatorService(
            validators=[
                container.resolve(FilenameExistsValidatorService),
                container.resolve(FilenameFormatValidatorService),
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
    container.register(BaseS3VideoService, S3VideoService)
    container.register(BaseVideoPresignedURLService, ORMVideoPresignedURLService)

    container.register(BaseVideoS3UploadValidatorService, VideoS3UploadExistsValidatorService)
    container.register(BaseVideoValidatorService, VideoExistsValidatorService)
    container.register(FilenameExistsValidatorService)
    container.register(FilenameFormatValidatorService)
    container.register(BaseFilenameValidatorService, factory=build_filename_validators)

    # init use cases
    container.register(LikeCreateUseCase)
    container.register(LikeDeleteUseCase)
    container.register(AbortMultipartUploadUseCase)
    container.register(InitiateMultipartUploadUseCase)
    container.register(GenerateUrlForUploadUseCase)
    container.register(CompleteUploadUseCase)
