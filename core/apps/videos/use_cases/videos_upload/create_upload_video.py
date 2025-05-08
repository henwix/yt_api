from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import BaseS3FileService
from core.apps.videos.services.s3_videos import BaseVideoFilenameValidatorService
from core.apps.videos.services.videos import BaseVideoService


User = get_user_model()


@dataclass
class CreateVideoMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    validator_service: BaseVideoFilenameValidatorService
    files_service: BaseS3FileService

    def execute(self, user: User, filename: str, validated_data: dict):
        #  validate filename
        self.validator_service.validate(filename=filename)

        #  Retrieve channel by user
        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        #  Create multipart upload
        upload_id, key = self.files_service.create_multipart_upload(
            filename=filename,
            data_type='video',
        )

        #  Add 'channel' and 'upload_id' in validated_data
        validated_data.update({'author': channel, 'upload_id': upload_id})

        #  Create video with 'validated_data' fields
        self.video_service.video_create(data=validated_data)

        return {'upload_id': upload_id, 'key': key}
