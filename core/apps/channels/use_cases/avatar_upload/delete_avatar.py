from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.channels.services.s3_channels import BaseAvatarValidatorService
from core.apps.common.services.files import BaseS3FileService


User = get_user_model()


@dataclass
class DeleteChannelAvatarUseCase:
    files_service: BaseS3FileService
    channel_service: BaseChannelService
    validator_service: BaseAvatarValidatorService

    def execute(self, user: User) -> dict:
        channel = self.channel_service.get_channel_by_user(user=user)
        self.validator_service.validate(channel)

        self.channel_service.update_avatar_fields_to_none(channel=channel)

        self.files_service.delete_object_by_key(key=channel.avatar_s3_key)

        return {'status': 'success'}
