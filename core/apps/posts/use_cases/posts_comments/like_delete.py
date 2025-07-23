from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.exceptions.comments import CommentLikeNotFoundError
from core.apps.posts.services.comments import BasePostCommentService
from core.apps.users.entities import UserEntity


@dataclass
class PostCommentLikeDeleteUseCase:
    comment_service: BasePostCommentService
    channel_service: BaseChannelService

    def execute(self, user: UserEntity, comment_id: int) -> dict:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)
        comment = self.comment_service.get_by_id_or_404(id=comment_id)

        deleted = self.comment_service.like_delete(
            author=channel,
            comment=comment,
        )

        if not deleted:
            raise CommentLikeNotFoundError(
                channel_slug=channel.slug,
                comment_id=comment_id,
            )
        return {'status': 'success'}
