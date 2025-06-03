from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.files import BaseS3FileService
from core.apps.users.entities import UserEntity
from core.apps.videos.services.videos import (
    BaseVideoAuthorValidatorService,
    BaseVideoService,
)


@dataclass
class GenerateUrlForVideoUploadUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    author_validator: BaseVideoAuthorValidatorService
    files_service: BaseS3FileService

    def execute(self, user: UserEntity, key: str, upload_id: str, part_number: int) -> str:
        author = self.channel_service.get_channel_by_user_or_404(user=user)
        video = self.video_service.get_video_by_upload_id(
            upload_id=upload_id,
        )
        self.author_validator.validate(video=video, author=author)

        url = self.files_service.generate_upload_part_url(
            key=key,
            upload_id=upload_id,
            part_number=part_number,
            expires_in=120,
        )

        return {'upload_url': url}
