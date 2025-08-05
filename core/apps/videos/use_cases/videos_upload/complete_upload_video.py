from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import BaseS3FileService
from core.apps.users.entities import UserEntity
from core.apps.videos.services.videos import (
    BaseVideoAuthorValidatorService,
    BaseVideoService,
)


@dataclass
class CompleteVideoMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    validator_service: BaseVideoAuthorValidatorService
    files_service: BaseS3FileService

    def execute(self, user: UserEntity, key: str, upload_id: str, parts: list) -> None:
        author = self.channel_service.get_channel_by_user_or_404(user=user)
        video = self.video_service.get_video_by_upload_id(
            upload_id=upload_id,
        )

        self.validator_service.validate(video=video, author=author)

        response = self.files_service.complete_multipart_upload(
            key=key,
            upload_id=upload_id,
            parts=parts,
        )

        self.video_service.update_video_after_upload(
            video_id=video.id,
            upload_id=upload_id,
            s3_key=response.get('Key'),
        )

        return {'detail': 'Success'}
