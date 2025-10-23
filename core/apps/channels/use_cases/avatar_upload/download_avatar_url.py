from dataclasses import dataclass

from core.apps.common.constants import CACHE_KEYS
from core.apps.common.services.files import BaseS3FileService


@dataclass
class GenerateUrlForAvatarDownloadUseCase:
    files_service: BaseS3FileService

    def execute(self, key: str) -> dict:
        url = self.files_service.generate_download_url(
            key=key,
            expires_in=3600,
            cache_key=CACHE_KEYS['s3_avatar_url'] + key,
        )

        return {'url': url}
