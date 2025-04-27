from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.boto_client import BaseBotoClientService
from core.apps.videos.services.videos import (
    BaseMultipartUploadVideoService,
    BaseVideoService,
)


User = get_user_model()


@dataclass
class InitiateMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    boto_service: BaseBotoClientService
    upload_service: BaseMultipartUploadVideoService

    def execute(self, user: User, name: str, description: str, status: str, filename: str):
        s3_client = self.boto_service.get_s3_client()
        bucket = self.boto_service.get_bucket_name()

        upload_id, key = self.upload_service.init_multipart_upload(
            s3_client=s3_client,
            bucket=bucket,
            filename=filename,
        )

        channel = self.channel_service.get_channel_by_user(user=user)
        self.video_service.video_create_s3(
            author=channel,
            name=name,
            description=description,
            status=status,
            upload_id=upload_id,
        )

        return upload_id, key
