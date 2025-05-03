import punq

from core.apps.videos.adapters.boto_file_provider import BotoFileProvider
from core.apps.videos.adapters.celery_file_provider import CeleryFileProvider
from core.apps.videos.providers.videos import (
    BaseBotoFileProvider,
    BaseCeleryFileProvider,
)
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
    BaseFilenameValidatorService,
    BaseS3FileService,
    BaseVideoS3UploadValidatorService,
    ComposedFilenameValidatorService,
    FilenameExistsValidatorService,
    FilenameFormatValidatorService,
    S3FileService,
    VideoS3UploadExistsValidatorService,
)
from core.apps.videos.services.videos import (
    BaseVideoHistoryService,
    BaseVideoPlaylistService,
    BaseVideoService,
    BaseVideoValidatorService,
    ORMVideoHistoryService,
    ORMVideoPlaylistService,
    ORMVideoService,
    VideoExistsValidatorService,
)
from core.apps.videos.use_cases.comments.like_create import LikeCreateUseCase
from core.apps.videos.use_cases.comments.like_delete import LikeDeleteUseCase
from core.apps.videos.use_cases.multipart_upload.abort_upload import AbortMultipartUploadUseCase
from core.apps.videos.use_cases.multipart_upload.complete_upload import CompleteUploadUseCase
from core.apps.videos.use_cases.multipart_upload.initiate_upload import InitiateMultipartUploadUseCase
from core.apps.videos.use_cases.multipart_upload.presigned_url_get_video import GenerateUrlForVideoRetrieveUseCase
from core.apps.videos.use_cases.multipart_upload.presigned_url_upload import GenerateUrlForUploadUseCase


def init_videos(container: punq.Container) -> None:
    def build_filename_validators() -> BaseFilenameValidatorService:
        return ComposedFilenameValidatorService(
            validators=[
                container.resolve(FilenameExistsValidatorService),
                container.resolve(FilenameFormatValidatorService),
            ],
        )

    # init providers
    container.register(BaseCeleryFileProvider, CeleryFileProvider)
    container.register(BaseBotoFileProvider, BotoFileProvider)

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
    container.register(BaseS3FileService, S3FileService)

    container.register(BaseVideoS3UploadValidatorService, VideoS3UploadExistsValidatorService)
    container.register(BaseVideoValidatorService, VideoExistsValidatorService)
    container.register(FilenameExistsValidatorService)
    container.register(FilenameFormatValidatorService)
    container.register(BaseFilenameValidatorService, factory=build_filename_validators)

    # init use cases
    container.register(LikeCreateUseCase)
    container.register(LikeDeleteUseCase)

    container.register(InitiateMultipartUploadUseCase)
    container.register(AbortMultipartUploadUseCase)
    container.register(CompleteUploadUseCase)
    container.register(GenerateUrlForUploadUseCase)
    container.register(GenerateUrlForVideoRetrieveUseCase)
