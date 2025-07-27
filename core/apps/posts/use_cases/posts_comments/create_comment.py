from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.posts.converters.comments import data_to_post_comment_entity
from core.apps.posts.entities.comments import PostCommentEntity
from core.apps.posts.entities.posts import PostEntity
from core.apps.posts.services.comments import BasePostCommentService
from core.apps.users.entities import UserEntity


@dataclass
class CreatePostCommentUseCase:
    channel_service: BaseChannelService
    post_comment_service: BasePostCommentService

    def execute(self, user: UserEntity, post: PostEntity, text: str, reply_comment_id: int | None) -> PostCommentEntity:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        comment = self.post_comment_service.create_comment(
            comment_entity=data_to_post_comment_entity(
                {
                    'text': text,
                    'author_id': channel.id,
                    'post_id': post.pk,
                    'reply_comment_id': reply_comment_id,
                },
            ),
        )

        return comment
