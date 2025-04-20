from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.services.channels import BaseChannelService
from core.apps.videos.services.comments import BaseCommentService


User = get_user_model()


@dataclass
class LikeCreateUseCase:
    comment_service: BaseCommentService
    channel_service: BaseChannelService

    def execute(self, user: User, comment_id: str, is_like: bool) -> dict:
        channel = self.channel_service.get_channel_by_user(user=user)
        comment = self.comment_service.get_by_id(id=comment_id)

        like, created = self.comment_service.like_get_or_create(
            channel=channel,
            comment=comment,
            is_like=is_like,
        )

        if not created and like.is_like != is_like:
            self.comment_service.change_like_status(like_id=like.pk, is_like=is_like)

        return {'status': 'success', 'is_like': is_like}
