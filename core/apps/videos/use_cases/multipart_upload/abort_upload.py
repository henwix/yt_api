from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.videos.services.upload import (
    BaseUploadIdValidatorService,
    BaseUploadKeyValidatorService,
    BaseVideoS3UploadValidatorService,
)
from core.apps.videos.services.videos import (
    BaseMultipartUploadVideoService,
    BaseVideoService,
)


User = get_user_model()


@dataclass
class AbortMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    upload_service: BaseMultipartUploadVideoService
    upload_id_validator_service: BaseUploadIdValidatorService
    upload_key_validator_service: BaseUploadKeyValidatorService
    video_upload_validator_service: BaseVideoS3UploadValidatorService

    def execute(self, user: User, key: str, upload_id: str):
        # validate 'upload_id' and 'key'
        self.upload_key_validator_service.validate(key=key)
        self.upload_id_validator_service.validate(upload_id=upload_id)

        # retrieve channel by user
        author = self.channel_service.get_channel_by_user(user=user)

        # retrieve video and validate
        video = self.video_service.get_video_by_upload_id_and_author(
            author=author,
            upload_id=upload_id,
        )
        self.video_upload_validator_service.validate(video=video, upload_id=upload_id)

        # abort multipart upload
        self.upload_service.abort_multipart_upload(
            key=key,
            upload_id=upload_id,
        )

        # delete video associated with 'upload_id'
        self.video_service.delete_video_by_id(video_id=video.video_id)

        return {'status': 'success'}
