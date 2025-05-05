from dataclasses import dataclass

from django.conf import settings

from core.apps.common.services.files import BaseS3FileService


@dataclass
class GenerateUrlForAvatarDownloadUseCase:
    files_service: BaseS3FileService

    def execute(self, key: str) -> dict:
        url = self.files_service.generate_download_url(
            key=key,
            expires_in=3600,
            cache_key=settings.CACHE_KEYS['s3_avatar_url'] + key,
        )

        return {'url': url}
