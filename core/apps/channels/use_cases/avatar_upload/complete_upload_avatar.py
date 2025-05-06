# TODO: протестить все эндпоинты
# TODO: добавить тесты


from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import (
    BaseFileExistsInS3ValidatorService,
    BaseS3FileService,
)


User = get_user_model()


@dataclass
class CompleteUploadAvatarUseCase:
    files_service: BaseS3FileService
    file_exists_validator: BaseFileExistsInS3ValidatorService
    channel_service: BaseChannelService

    def execute(self, key: str, user: User) -> dict:
        self.file_exists_validator.validate(key=key)

        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        self.channel_service.set_avatar_s3_key(
            channel=channel,
            avatar_s3_key=key,
        )

        return {'status': 'success'}
