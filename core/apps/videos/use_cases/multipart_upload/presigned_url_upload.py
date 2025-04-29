from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.videos.services.upload import BaseVideoS3UploadValidatorService
from core.apps.videos.services.videos import (
    BaseS3VideoService,
    BaseVideoService,
)


User = get_user_model()


@dataclass
class GenerateUrlForUploadUseCase:
    s3_video_service: BaseS3VideoService
    video_service: BaseVideoService
    channel_service: BaseChannelService
    video_upload_validator_service: BaseVideoS3UploadValidatorService

    def execute(self, user: User, key: str, upload_id: str, part_number: int) -> str:
        author = self.channel_service.get_channel_by_user(user=user)
        video = self.video_service.get_video_by_upload_id_and_author(
            author=author,
            upload_id=upload_id,
        )
        self.video_upload_validator_service.validate(video=video, upload_id=upload_id)

        url = self.s3_video_service.generate_upload_part_url(
            key=key,
            upload_id=upload_id,
            part_number=part_number,
        )

        return {'upload_url': url}
