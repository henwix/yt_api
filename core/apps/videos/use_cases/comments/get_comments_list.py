from dataclasses import dataclass
from typing import Iterable

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.entities import UserEntity
from core.apps.videos.models import VideoComment
from core.apps.videos.services.comments import BaseVideoCommentService
from core.apps.videos.services.videos import (
    BasePrivateVideoPermissionValidatorService,
    BaseVideoService,
)


@dataclass
class GetVideoCommentsUseCase:
    channel_service: BaseChannelService
    video_service: BaseVideoService
    comment_service: BaseVideoCommentService
    validator_service: BasePrivateVideoPermissionValidatorService

    def execute(self, user: UserEntity, video_id: str) -> Iterable[VideoComment]:
        channel = self.channel_service.get_channel_by_user_or_none(user)
        video = self.video_service.get_video_by_id_or_404(video_id)

        self.validator_service.validate(video, channel)

        qs = self.comment_service.get_comments_by_video_id(
            video_id=video_id,
        )

        return qs
