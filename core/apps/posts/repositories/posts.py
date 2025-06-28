from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.posts.converters.likes import post_like_to_entity
from core.apps.posts.converters.posts import post_to_entity
from core.apps.posts.entities.likes import PostLikeEntity
from core.apps.posts.entities.posts import PostEntity
from core.apps.posts.models import (
    Post,
    PostLikeItem,
)


class BasePostRepository(ABC):
    @abstractmethod
    def create_post(self, post_entity: PostEntity) -> PostEntity:
        ...

    @abstractmethod
    def get_all_posts(self) -> Iterable[Post]:
        ...

    @abstractmethod
    def get_post_by_id(self, post_id: str) -> PostEntity | None:
        ...

    @abstractmethod
    def like_get_or_create(
        self,
        channel: ChannelEntity,
        post: PostEntity,
        is_like: bool,
    ) -> tuple[PostLikeEntity, bool]:
        ...

    @abstractmethod
    def like_delete(self, channel: ChannelEntity, post: PostEntity) -> bool:
        ...

    @abstractmethod
    def update_is_like_field(like: PostLikeEntity, is_like: bool) -> None:
        ...


class PostRepository(BasePostRepository):
    def create_post(self, post_entity: PostEntity) -> PostEntity:
        post_dto = Post.objects.create(**post_entity.__dict__)
        return post_to_entity(post=post_dto)

    def get_all_posts(self) -> Iterable[Post]:
        return Post.objects.all()

    def get_post_by_id(self, post_id: str) -> PostEntity | None:
        post_dto = Post.objects.filter(pk=post_id).first()
        return post_to_entity(post=post_dto) if post_dto else None

    def like_get_or_create(
        self,
        channel: ChannelEntity,
        post: PostEntity,
        is_like: bool,
    ) -> tuple[PostLikeEntity, bool]:
        like, created = PostLikeItem.objects.get_or_create(
            channel_id=channel.id,
            post_id=post.pk,
            defaults={'is_like': is_like},
        )
        return post_like_to_entity(like), created

    def like_delete(self, channel: ChannelEntity, post: PostEntity) -> bool:
        deleted, _ = PostLikeItem.objects.filter(channel_id=channel.id, post_id=post.pk).delete()
        return True if deleted else False

    def update_is_like_field(self, like: PostLikeEntity, is_like: bool) -> None:
        PostLikeItem.objects.filter(pk=like.id).update(is_like=is_like)
