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
from core.apps.videos.entities.comments import VideoCommentEntity
from core.apps.videos.entities.likes import VideoCommentLikeItemEntity
from core.apps.videos.models import (
    Video,
    VideoComment,
)
from core.apps.videos.repositories.comments import BaseVideoCommentRepository


@dataclass
class BaseVideoCommentService(ABC):
    repository: BaseVideoCommentRepository

    @abstractmethod
    def create_comment(self, comment_entity: VideoCommentEntity) -> VideoCommentEntity: ...

    @abstractmethod
    def get_comments_by_video_id(self, video_id: str) -> Iterable[VideoComment]: ...

    @abstractmethod
    def get_replies_by_comment_id(self, comment_id: str) -> Iterable[VideoComment]: ...

    @abstractmethod
    def get_by_id_or_404(self, id: str) -> VideoCommentEntity: ...

    @abstractmethod
    def change_updated_status(self, comment_id: str, is_updated: bool) -> None: ...

    @abstractmethod
    def update_like_status(self, like_id: int, is_like: bool) -> None: ...

    @abstractmethod
    def like_get_or_create(
        self,
        author: ChannelEntity,
        comment: VideoCommentEntity,
        is_like: bool,
    ) -> tuple[VideoCommentLikeItemEntity, bool]: ...

    @abstractmethod
    def like_delete(self, author: ChannelEntity, comment: VideoCommentEntity) -> bool: ...


class ORMCommentService(BaseVideoCommentService):
    def _build_query(self, queryset: Iterable[VideoComment]) -> Iterable[VideoComment]:
        return (
            queryset.select_related('author', 'video')
            .filter(video__upload_status=Video.UploadStatus.FINISHED)
            .annotate(
                likes_count=Count('likes', distinct=True, filter=Q(likes_items__is_like=True)),
                replies_count=Count('replies', distinct=True),
            )
        )

    def create_comment(self, comment_entity: VideoCommentEntity) -> VideoCommentEntity:
        comment_entity.update_reply_level()
        return self.repository.create_comment(comment_entity=comment_entity)

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
        qs = self._build_query(queryset=self.repository.get_all_comments())
        return qs.filter(
            video__video_id=video_id,
            reply_comment__isnull=True,
            reply_level=0,
        )

    def get_replies_by_comment_id(self, comment_id: str) -> Iterable[VideoComment]:
        if not comment_id:
            raise CommentNotFoundError()

        qs = self._build_query(queryset=self.repository.get_all_comments())
        return qs.filter(reply_comment_id=comment_id, reply_level=1)

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
