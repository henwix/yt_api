from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.entities import UserEntity
from core.apps.videos.converters.comments import data_to_video_comment_entity
from core.apps.videos.entities.comments import VideoCommentEntity
from core.apps.videos.entities.videos import VideoEntity
from core.apps.videos.services.comments import BaseVideoCommentService
from core.apps.videos.services.videos import BaseVideoPrivateOrUploadingValidatorService


@dataclass
class CreateVideoCommentUseCase:
    channel_service: BaseChannelService
    video_comment_service: BaseVideoCommentService
    video_validator: BaseVideoPrivateOrUploadingValidatorService

    def execute(
        self,
        user: UserEntity,
        video: VideoEntity,
        text: str,
        reply_comment_id: int | None,
    ) -> VideoCommentEntity:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        self.video_validator.validate(video=video, channel=channel)

        comment = self.video_comment_service.create_comment(
            comment_entity=data_to_video_comment_entity(
                {
                    'text': text,
                    'author_id': channel.id,
                    'video_id': video.id,
                    'reply_comment_id': reply_comment_id,
                },
            ),
        )

        return comment
