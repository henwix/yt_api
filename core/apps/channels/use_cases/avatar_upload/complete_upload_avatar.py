# TODO: Может быть закрыть бакет на приватный доступ, и выдавать только закрытый URL?
# TODO: мб сейвить presigned_url в базе сразу после его генерации, чтобы не запрашивать его каждый раз, хоть и из кэша?
# TODO: протестить все эндпоинты
# TODO: добавить тесты
# TODO: сделать -amend ласт коммита с инфой про изменения

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

        channel = self.channel_service.get_channel_by_user(user=user)

        # TODO: почему-то не отправляется сигнал на очистку кэша при обновлении ключа
        self.channel_service.set_avatar_s3_key(
            channel_pk=channel.pk,
            avatar_s3_key=key,
        )

        return {'status': 'success'}
