from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.entities import UserEntity
from core.apps.videos.services.comments import BaseVideoCommentService


@dataclass
class VideoCommentLikeCreateUseCase:
    comment_service: BaseVideoCommentService
    channel_service: BaseChannelService

    def execute(self, user: UserEntity, comment_id: str, is_like: bool) -> dict:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)
        comment = self.comment_service.get_by_id_or_404(id=comment_id)

        like, created = self.comment_service.like_get_or_create(
            author=channel,
            comment=comment,
            is_like=is_like,
        )

        if not created and like.is_like != is_like:
            self.comment_service.update_like_status(like_id=like.id, is_like=is_like)

        return {'detail': 'Success', 'is_like': is_like}
