from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.videos.services.upload import BaseFilenameValidatorService
from core.apps.videos.services.videos import (
    BaseMultipartUploadVideoService,
    BaseVideoService,
)


User = get_user_model()


@dataclass
class InitiateMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    upload_service: BaseMultipartUploadVideoService
    validator_service: BaseFilenameValidatorService

    def execute(self, user: User, filename: str, validated_data: dict):
        #  validate filename
        self.validator_service.validate(filename=filename)

        #  Retrieve channel by user
        channel = self.channel_service.get_channel_by_user(user=user)

        #  Initiate multipart upload
        upload_id, key = self.upload_service.init_multipart_upload(
            filename=filename,
        )

        #  Add 'channel' and 'upload_id' in validated_data
        validated_data.update({'author': channel, 'upload_id': upload_id})

        #  Create video with 'validated_data' fields
        self.video_service.video_create_s3(validated_data=validated_data)

        return upload_id, key
