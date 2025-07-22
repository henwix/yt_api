from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.posts.converters.comments import post_comment_to_entity
from core.apps.posts.entities.comments import PostCommentEntity
from core.apps.posts.models import PostCommentItem


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


class PostCommentRepository(BasePostCommentRepository):
    def create_comment(self, comment_entity: PostCommentEntity) -> PostCommentEntity:
        # comment_dto = video_comment_from_entity(comment_entity).save()
        comment_dto = PostCommentItem.objects.create(**comment_entity.__dict__)
        return post_comment_to_entity(comment_dto)

    def get_all_comments(self) -> Iterable[PostCommentItem]:
        return PostCommentItem.objects.all()

    def change_updated_status(self, comment_id: str, is_updated: bool):
        PostCommentItem.objects.filter(pk=comment_id).update(is_updated=is_updated)
