from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.posts.converters.comments import post_comment_to_entity
from core.apps.posts.converters.likes import post_comment_like_item_to_entity
from core.apps.posts.entities.comments import PostCommentEntity
from core.apps.posts.entities.likes import PostCommentLikeItemEntity
from core.apps.posts.models import (
    PostCommentItem,
    PostCommentLikeItem,
)


class BasePostCommentRepository(ABC):
    @abstractmethod
    def create_comment(self, comment_entity: PostCommentEntity) -> PostCommentEntity:
        ...

    @abstractmethod
    def get_all_comments(self) -> Iterable[PostCommentItem]:
        ...

    @abstractmethod
    def change_updated_status(self, comment_id: str, is_updated: bool) -> None:
        ...

    @abstractmethod
    def get_by_id_or_none(self, id: int) -> PostCommentEntity | None:
        ...

    @abstractmethod
    def like_get_or_create(
        self,
        author: ChannelEntity,
        comment: PostCommentEntity,
        is_like: bool,
    ) -> tuple[PostCommentLikeItemEntity, bool]:
        ...

    @abstractmethod
    def like_delete(self, author: ChannelEntity, comment: PostCommentEntity) -> bool:
        ...

    @abstractmethod
    def update_like_status(self, like_id: int, is_like: bool) -> None:
        ...


class PostCommentRepository(BasePostCommentRepository):
    def create_comment(self, comment_entity: PostCommentEntity) -> PostCommentEntity:
        # comment_dto = video_comment_from_entity(comment_entity).save()
        comment_dto = PostCommentItem.objects.create(**comment_entity.__dict__)
        return post_comment_to_entity(comment_dto)

    def get_all_comments(self) -> Iterable[PostCommentItem]:
        return PostCommentItem.objects.all()

    def change_updated_status(self, comment_id: str, is_updated: bool):
        PostCommentItem.objects.filter(pk=comment_id).update(is_updated=is_updated)

    def get_by_id_or_none(self, id: int) -> PostCommentEntity | None:
        comment_dto = PostCommentItem.objects.filter(id=id).first()
        return post_comment_to_entity(comment_dto) if comment_dto else None

    def like_get_or_create(
        self,
        author: ChannelEntity,
        comment: PostCommentEntity,
        is_like: bool,
    ) -> tuple[PostCommentLikeItemEntity, bool]:
        like_dto, created = PostCommentLikeItem.objects.get_or_create(
            author_id=author.id,
            comment_id=comment.id,
            defaults={'is_like': is_like},
        )
        return post_comment_like_item_to_entity(like_dto), created

    def like_delete(self, author: ChannelEntity, comment: PostCommentEntity) -> bool:
        deleted, _ = PostCommentLikeItem.objects.filter(
            author_id=author.id,
            comment_id=comment.id,
        ).delete()

        return True if deleted else False

    def update_like_status(self, like_id: int, is_like: bool) -> None:
        PostCommentLikeItem.objects.filter(id=like_id).update(is_like=is_like)
