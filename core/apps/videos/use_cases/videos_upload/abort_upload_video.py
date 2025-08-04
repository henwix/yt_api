from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import (
    BaseMultipartUploadExistsInS3ValidatorService,
    BaseS3FileService,
)
from core.apps.users.entities import UserEntity
from core.apps.videos.services.videos import (
    BaseVideoAuthorValidatorService,
    BaseVideoService,
)


@dataclass
class AbortVideoMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    video_validator_service: BaseVideoAuthorValidatorService
    upload_validator_service: BaseMultipartUploadExistsInS3ValidatorService
    files_service: BaseS3FileService

    def execute(self, user: UserEntity, key: str, upload_id: str):
        # validate if the multipart upload exists is S3
        self.upload_validator_service.validate(key=key, upload_id=upload_id)

        # retrieve video
        video = self.video_service.get_video_by_upload_id(
            upload_id=upload_id,
        )

        # retrieve channel by user
        author = self.channel_service.get_channel_by_user_or_404(user=user)

        # validate video
        self.video_validator_service.validate(video=video, author=author)

        # abort multipart upload
        self.files_service.abort_multipart_upload(
            key=key,
            upload_id=upload_id,
        )

        # delete video associated with 'upload_id'
        self.video_service.delete_video_by_id(video_id=video.id)

        return {'detail': 'Success'}
