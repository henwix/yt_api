from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.posts.exceptions import PostLikeNotFoundError
from core.apps.posts.services.posts import BasePostService
from core.apps.users.entities import UserEntity


@dataclass
class PostLikeDeleteUseCase:
    channel_service: BaseChannelService
    post_service: BasePostService

    def execute(self, user: UserEntity, post_id: str) -> dict:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)
        post = self.post_service.get_post_by_id_or_404(post_id=post_id)

        deleted = self.post_service.like_delete(channel, post)

        if not deleted:
            raise PostLikeNotFoundError(channel_slug=channel.slug, post_id=post.pk)

        return {'status': 'success'}
