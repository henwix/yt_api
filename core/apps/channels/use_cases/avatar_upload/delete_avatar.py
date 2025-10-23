from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.channels.services.s3_channels import BaseAvatarValidatorService
from core.apps.common.constants import CACHE_KEYS
from core.apps.common.services.files import BaseS3FileService
from core.apps.users.entities import UserEntity


@dataclass
class DeleteChannelAvatarUseCase:
    files_service: BaseS3FileService
    channel_service: BaseChannelService
    validator_service: BaseAvatarValidatorService

    def execute(self, user: UserEntity) -> dict:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)
        self.validator_service.validate(channel=channel)

        self.files_service.delete_object_by_key(
            key=channel.avatar_s3_key,
            cache_key=CACHE_KEYS['s3_avatar_url'] + channel.avatar_s3_key,
        )

        self.channel_service.set_avatar_s3_key(
            channel=channel,
            avatar_s3_key=None,
        )

        return {'detail': 'Success'}
