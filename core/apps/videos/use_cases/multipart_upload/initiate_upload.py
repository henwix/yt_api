from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.videos.services.s3_videos import (
    BaseFilenameValidatorService,
    BaseS3FileService,
)
from core.apps.videos.services.videos import BaseVideoService


User = get_user_model()


# TODO: включить версионирование + учитывать при создании файлов версию этого файла(VersionId)
@dataclass
class InitiateMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    s3_video_service: BaseS3FileService
    validator_service: BaseFilenameValidatorService

    def execute(self, user: User, filename: str, validated_data: dict):
        #  validate filename
        self.validator_service.validate(filename=filename)

        #  Retrieve channel by user
        channel = self.channel_service.get_channel_by_user(user=user)

        #  Initiate multipart upload
        upload_id, key = self.s3_video_service.init_multipart_upload(
            filename=filename,
        )

        #  Add 'channel' and 'upload_id' in validated_data
        validated_data.update({'author': channel, 'upload_id': upload_id})

        #  Create video with 'validated_data' fields
        self.video_service.video_create(validated_data=validated_data)

        return {'upload_id': upload_id, 'key': key}
