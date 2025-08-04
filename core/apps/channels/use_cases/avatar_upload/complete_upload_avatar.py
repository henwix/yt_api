from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import (
    BaseFileExistsInS3ValidatorService,
    BaseS3FileService,
)
from core.apps.users.entities import UserEntity


@dataclass
class CompleteUploadAvatarUseCase:
    files_service: BaseS3FileService
    file_exists_validator: BaseFileExistsInS3ValidatorService
    channel_service: BaseChannelService

    def execute(self, key: str, user: UserEntity) -> dict:
        self.file_exists_validator.validate(key=key)

        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        self.channel_service.set_avatar_s3_key(
            channel=channel,
            avatar_s3_key=key,
        )

        return {'detail': 'Success'}
