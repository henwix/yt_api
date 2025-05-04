from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import BaseS3FileService
from core.apps.videos.services.s3_videos import BaseUploadVideoValidatorService
from core.apps.videos.services.videos import BaseVideoService


User = get_user_model()


@dataclass
class AbortVideoMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    video_upload_validator_service: BaseUploadVideoValidatorService
    files_service: BaseS3FileService

    def execute(self, user: User, key: str, upload_id: str):
        # retrieve channel by user
        author = self.channel_service.get_channel_by_user(user=user)

        # retrieve video and validate
        video = self.video_service.get_video_by_upload_id_and_author(
            author=author,
            upload_id=upload_id,
        )
        self.video_upload_validator_service.validate(video=video, upload_id=upload_id)

        # abort multipart upload
        self.files_service.abort_multipart_upload(
            key=key,
            upload_id=upload_id,
        )

        # delete video associated with 'upload_id'
        self.video_service.delete_video_by_id(video_id=video.video_id)

        return {'status': 'success'}
