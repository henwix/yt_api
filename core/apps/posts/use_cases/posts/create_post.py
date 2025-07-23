from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.posts.converters.posts import data_to_post_entity
from core.apps.posts.entities.posts import PostEntity
from core.apps.posts.services.posts import BasePostService
from core.apps.users.entities import UserEntity


@dataclass
class PostCreateUseCase:
    channel_service: BaseChannelService
    post_service: BasePostService

    def execute(self, user: UserEntity, text: str) -> PostEntity:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        post = self.post_service.create_post(
            post_entity=data_to_post_entity(
                {
                    'author_id': channel.id,
                    'text': text,
                },
            ),
        )

        return post
