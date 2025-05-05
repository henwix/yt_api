from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import (
    BaseFileExistsInS3ValidatorService,
    BaseS3FileService,
)
from core.apps.videos.services.videos import (
    BaseVideoAuthorValidatorService,
    BaseVideoService,
)


User = get_user_model()


@dataclass
class CompleteVideoMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    validator_service: BaseVideoAuthorValidatorService
    files_service: BaseS3FileService
    file_exists_validator: BaseFileExistsInS3ValidatorService

    def execute(self, user: User, key: str, upload_id: str, parts: list) -> None:
        author = self.channel_service.get_channel_by_user(user=user)
        video = self.video_service.get_video_by_upload_id(
            upload_id=upload_id,
        )

        self.validator_service.validate(video=video, author=author)

        self.file_exists_validator.validate(key=key)

        response = self.files_service.complete_multipart_upload(
            key=key,
            upload_id=upload_id,
            parts=parts,
        )

        self.video_service.update_video_after_upload(
            video_id=video.video_id,
            upload_id=upload_id,
            s3_key=response.get('Key'),
        )

        return {'status': 'success', 'message': 'Video upload completed successfully.'}
