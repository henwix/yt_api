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

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.videos.entities.comments import VideoCommentEntity
from core.apps.videos.entities.likes import VideoCommentLikeItemEntity
from core.apps.videos.exceptions.comments import CommentNotFoundError
from core.apps.videos.exceptions.videos import VideoNotFoundByVideoIdError
from core.apps.videos.models import VideoComment
from core.apps.videos.repositories.comments import BaseVideoCommentRepository


@dataclass
class BaseCommentService(ABC):
    repository: BaseVideoCommentRepository

    @abstractmethod
    def get_comments_by_video_id(self, video_id: str) -> Iterable[VideoComment]:
        ...

    @abstractmethod
    def get_replies_by_comment_id(self, comment_id: str) -> Iterable[VideoComment]:
        ...

    @abstractmethod
    def get_by_id_or_404(self, id: str) -> VideoCommentEntity:
        ...

    @abstractmethod
    def change_updated_status(self, comment_id: str, is_updated: bool) -> None:
        ...

    @abstractmethod
    def update_like_status(self, like_id: int, is_like: bool) -> None:
        ...

    @abstractmethod
    def like_get_or_create(
        self,
        author: ChannelEntity,
        comment: VideoCommentEntity,
        is_like: bool,
    ) -> tuple[VideoCommentLikeItemEntity, bool]:
        ...

    @abstractmethod
    def like_delete(self, author: ChannelEntity, comment: VideoCommentEntity) -> bool:
        ...


class ORMCommentService(BaseCommentService):
    def _build_query(self, queryset: Iterable[VideoComment]) -> Iterable[VideoComment]:
        return queryset.select_related('author', 'video').annotate(
            likes_count=Count('likes', distinct=True, filter=Q(likes_items__is_like=True)),
            replies_count=Count('replies', distinct=True),
        )

    def get_related_queryset(self) -> Iterable[VideoComment]:
        return self._build_query(
            queryset=self.repository.get_all_comments(),
        )

    def get_annotated_queryset(self) -> Iterable[VideoComment]:
        return self.repository.get_all_comments().annotate(
            likes_count=Count('likes', distinct=True, filter=Q(likes_items__is_like=True)),
            replies_count=Count('replies', distinct=True),
        )

    def get_comments_by_video_id(self, video_id: str) -> Iterable[VideoComment]:
        if not video_id:
            raise VideoNotFoundByVideoIdError(video_id=video_id)

        qs = self._build_query(queryset=self.repository.get_all_comments())
        return qs.filter(
            video__video_id=video_id, comment__isnull=True, reply_level=0,
        )

    def get_replies_by_comment_id(self, comment_id: str) -> Iterable[VideoComment]:
        if not comment_id:
            raise CommentNotFoundError()

        qs = self._build_query(queryset=self.repository.get_all_comments())
        return qs.select_related('comment').filter(comment_id=comment_id)

    def change_updated_status(self, comment_id: str, is_updated: bool) -> None:
        self.repository.change_updated_status(comment_id=comment_id, is_updated=is_updated)

    def get_by_id_or_404(self, id: str) -> VideoCommentEntity:
        comment = self.repository.get_by_id_or_none(id=id)

        if comment is None:
            raise CommentNotFoundError()

        return comment

    def update_like_status(self, like_id: int, is_like: bool) -> None:
        self.repository.update_like_status(like_id=like_id, is_like=is_like)

    def like_get_or_create(
        self,
        author: ChannelEntity,
        comment: VideoCommentEntity,
        is_like: bool,
    ) -> tuple[VideoCommentLikeItemEntity, bool]:
        like, created = self.repository.like_get_or_create(
            author=author,
            comment=comment,
            is_like=is_like,
        )
        return like, created

    def like_delete(self, author: ChannelEntity, comment: VideoCommentEntity) -> bool:
        deleted = self.repository.like_delete(
            author=author,
            comment=comment,
        )
        return deleted
