from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import BaseS3FileService
from core.apps.videos.services.videos import (
    BasePrivateVideoPermissionValidatorService,
    BaseVideoService,
)


User = get_user_model()


@dataclass
class GenerateUrlForVideoDownloadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    files_service: BaseS3FileService
    permission_validator: BasePrivateVideoPermissionValidatorService

    def execute(self, user: User, key: str) -> dict:
        channel = self.channel_service.get_channel_by_user_or_none(user=user)
        video = self.video_service.get_video_by_key(key=key)

        self.permission_validator.validate(video=video, channel=channel)

        url = self.files_service.generate_download_url(
            key=video.s3_key,
            expires_in=3600,
            cache_key=settings.CACHE_KEYS['s3_video_url'] + key,
        )

        return {'url': url}
