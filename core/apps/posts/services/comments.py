from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable
from dataclasses import dataclass

from django.db.models import (
    Count,
    Q,
)

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.common.exceptions.comments import CommentNotFoundError
from core.apps.posts.entities.comments import PostCommentEntity
from core.apps.posts.entities.likes import PostCommentLikeItemEntity
from core.apps.posts.models import PostCommentItem
from core.apps.posts.repositories.comments import BasePostCommentRepository


@dataclass
class BasePostCommentService(ABC):
    repository: BasePostCommentRepository

    @abstractmethod
    def create_comment(self, comment_entity: PostCommentEntity) -> PostCommentEntity: ...

    @abstractmethod
    def get_by_id_or_404(self, id: int) -> PostCommentEntity: ...

    @abstractmethod
    def like_get_or_create(
        self,
        author: ChannelEntity,
        comment: PostCommentEntity,
        is_like: bool,
    ) -> tuple[PostCommentLikeItemEntity, bool]: ...

    @abstractmethod
    def like_delete(self, author: ChannelEntity, comment: PostCommentEntity) -> bool: ...

    @abstractmethod
    def update_like_status(self, like_id: int, is_like: bool) -> None: ...

    @abstractmethod
    def get_all_comments(self) -> Iterable[PostCommentItem]: ...

    @abstractmethod
    def get_comments_for_retrieving(self) -> Iterable[PostCommentItem]: ...

    @abstractmethod
    def get_replies_by_comment_id(self, comment_id: int) -> Iterable[PostCommentItem]: ...

    @abstractmethod
    def change_updated_status(self, comment_id: int, is_updated: bool) -> None: ...

    @abstractmethod
    def get_comments_by_post_id(self, post_id: str) -> Iterable[PostCommentItem]: ...


class PostCommentService(BasePostCommentService):
    def _build_query(self, qs: Iterable[PostCommentItem]) -> Iterable[PostCommentItem]:
        return qs.select_related('author').annotate(
            likes_count=Count('likes', distinct=True, filter=Q(likes_items__is_like=True)),
            replies_count=Count('replies', distinct=True),
        )

    def create_comment(self, comment_entity: PostCommentEntity) -> PostCommentEntity:
        comment_entity.update_reply_level()
        return self.repository.create_comment(comment_entity=comment_entity)

    def get_by_id_or_404(self, id: int) -> PostCommentEntity:
        comment = self.repository.get_by_id_or_none(id=id)

        if comment is None:
            raise CommentNotFoundError()

        return comment

    def like_get_or_create(
        self,
        author: ChannelEntity,
        comment: PostCommentEntity,
        is_like: bool,
    ) -> tuple[PostCommentLikeItemEntity, bool]:
        like, created = self.repository.like_get_or_create(
            author=author,
            comment=comment,
            is_like=is_like,
        )
        return like, created

    def like_delete(self, author: ChannelEntity, comment: PostCommentEntity) -> bool:
        deleted = self.repository.like_delete(
            author=author,
            comment=comment,
        )
        return deleted

    def update_like_status(self, like_id: int, is_like: bool) -> None:
        self.repository.update_like_status(like_id=like_id, is_like=is_like)

    def get_all_comments(self) -> Iterable[PostCommentItem]:
        return self.repository.get_all_comments()

    def get_comments_for_retrieving(self) -> Iterable[PostCommentItem]:
        qs = self.repository.get_all_comments()
        return self._build_query(qs=qs)

    def get_replies_by_comment_id(self, comment_id: int) -> Iterable[PostCommentItem]:
        qs = self._build_query(qs=self.repository.get_all_comments())
        return qs.filter(reply_level=1, reply_comment_id=comment_id)

    def change_updated_status(self, comment_id: int, is_updated: bool) -> None:
        self.repository.change_updated_status(comment_id=comment_id, is_updated=is_updated)

    def get_comments_by_post_id(self, post_id: str) -> Iterable[PostCommentItem]:
        qs = self._build_query(qs=self.repository.get_all_comments())
        return qs.filter(
            post__post_id=post_id,
            reply_comment__isnull=True,
            reply_level=0,
        )
