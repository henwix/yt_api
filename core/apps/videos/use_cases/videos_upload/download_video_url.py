from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.constants import CACHE_KEYS
from core.apps.common.services.files import BaseS3FileService
from core.apps.users.entities import (
    AnonymousUserEntity,
    UserEntity,
)
from core.apps.videos.services.videos import (
    BasePrivateVideoPermissionValidatorService,
    BaseVideoService,
)


@dataclass
class GenerateUrlForVideoDownloadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    files_service: BaseS3FileService
    permission_validator: BasePrivateVideoPermissionValidatorService

    def execute(self, user: UserEntity | AnonymousUserEntity, key: str) -> dict:
        channel = self.channel_service.get_channel_by_user_or_none(user=user)
        video = self.video_service.get_video_by_key(key=key)

        self.permission_validator.validate(video=video, channel=channel)

        url = self.files_service.generate_download_url(
            key=video.s3_key,
            expires_in=3600,
            cache_key=CACHE_KEYS['s3_video_url'] + key,
        )

        return {'url': url}
