from dataclasses import dataclass

from core.apps.common.services.files import BaseS3FileService
from core.apps.videos.services.videos import BaseVideoService


@dataclass
class GenerateUrlForVideoDownloadUseCase:
    video_service: BaseVideoService
    files_service: BaseS3FileService

    def execute(self, key: str) -> dict:
        video = self.video_service.get_public_video_by_key(key=key)
        url = self.files_service.generate_download_url(
            key=video.s3_key,
            expires_in=3600,
            cache_key=f's3_video_url_{key}',
        )

        return {'url': url}
