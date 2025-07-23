from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.posts.services.posts import BasePostService
from core.apps.users.entities import UserEntity


@dataclass
class PostLikeCreateUseCase:
    channel_service: BaseChannelService
    post_service: BasePostService

    def execute(self, user: UserEntity, post_id: str, is_like: bool) -> dict:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)
        post = self.post_service.get_post_by_id_or_404(post_id=post_id)

        like, created = self.post_service.like_get_or_create(channel, post, is_like)

        if not created and like.is_like != is_like:
            self.post_service.update_is_like_field(like, is_like)

        return {'status': 'success', 'is_like': is_like}
