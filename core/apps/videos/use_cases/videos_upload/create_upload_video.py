from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import BaseS3FileService
from core.apps.users.entities import UserEntity
from core.apps.videos.converters.videos import data_to_video_entity
from core.apps.videos.services.s3_videos import BaseVideoFilenameValidatorService
from core.apps.videos.services.videos import BaseVideoService


@dataclass
class CreateVideoMultipartUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    validator_service: BaseVideoFilenameValidatorService
    files_service: BaseS3FileService

    def execute(self, user: UserEntity, filename: str, validated_data: dict) -> dict:
        #  validate filename
        self.validator_service.validate(filename=filename)

        #  Retrieve channel by user
        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        #  Create multipart upload
        upload_id, key = self.files_service.create_multipart_upload(
            filename=filename,
            data_type='video',
        )
        #  Add 'channel_id' and 'upload_id' in validated_data
        validated_data.update({'author_id': channel.id, 'upload_id': upload_id})

        #  Create video with 'validated_data' fields
        self.video_service.video_create(video_entity=data_to_video_entity(validated_data))

        return {'upload_id': upload_id, 'key': key}
