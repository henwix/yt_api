from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from django.db.models import (
    Count,
    Q,
)

from core.apps.posts.entities.comments import PostCommentEntity
from core.apps.posts.models import PostCommentItem
from core.apps.posts.repositories.comments import BasePostCommentRepository


@dataclass
class BasePostCommentService(ABC):
    repository: BasePostCommentRepository

    @abstractmethod
    def create_comment(self, comment_entity: PostCommentEntity) -> PostCommentEntity:
        ...

    @abstractmethod
    def get_all_comments(self) -> Iterable[PostCommentItem]:
        ...

    @abstractmethod
    def get_comments_for_retrieving(self) -> Iterable[PostCommentItem]:
        ...

    @abstractmethod
    def change_updated_status(self, comment_id: str, is_updated: bool) -> None:
        ...

    @abstractmethod
    def get_comments_by_post_id(self, post_id: str) -> Iterable[PostCommentItem]:
        ...


class PostCommentService(BasePostCommentService):
    def _build_query(self, qs: Iterable[PostCommentItem]) -> Iterable[PostCommentItem]:
        return qs.select_related('author').annotate(
            likes_count=Count("likes", distinct=True, filter=Q(likes_items__is_like=True)),
            replies_count=Count("replies", distinct=True),
        )

    def create_comment(self, comment_entity: PostCommentEntity) -> PostCommentEntity:
        comment_entity.update_reply_level()
        return self.repository.create_comment(comment_entity=comment_entity)

    def get_all_comments(self) -> Iterable[PostCommentItem]:
        return self.repository.get_all_comments()

    def get_comments_for_retrieving(self) -> Iterable[PostCommentItem]:
        qs = self.repository.get_all_comments()
        return self._build_query(qs=qs)

    def change_updated_status(self, comment_id: str, is_updated: bool) -> None:
        self.repository.change_updated_status(comment_id=comment_id, is_updated=is_updated)

    def get_comments_by_post_id(self, post_id: str) -> Iterable[PostCommentItem]:
        qs = self._build_query(qs=self.repository.get_all_comments())
        return qs.filter(
            post__post_id=post_id,
            reply_comment__isnull=True,
            reply_level=0,
        )
