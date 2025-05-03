from dataclasses import dataclass

from core.apps.videos.services.s3_videos import BaseS3FileService
from core.apps.videos.services.videos import BaseVideoService


@dataclass
class GenerateUrlForVideoRetrieveUseCase:
    video_service: BaseVideoService
    s3_video_service: BaseS3FileService

    def execute(self, key: str) -> dict:
        expires_in = 3600

        video = self.video_service.get_public_video_by_key(key=key)
        url = self.s3_video_service.generate_download_url(key=video.s3_key, expires_in=expires_in)

        return {'url': url}
