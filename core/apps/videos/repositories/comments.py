from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.channels.models import Channel
from core.apps.videos.models import (
    VideoComment,
    VideoCommentLikeItem,
)


class BaseVideoCommentRepository(ABC):
    @abstractmethod
    def get_all_comments(self) -> Iterable[VideoComment]:
        ...

    @abstractmethod
    def change_comment_updated_status(self, comment_id: str) -> None:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> VideoComment:
        ...

    @abstractmethod
    def like_get_or_create(self, channel: Channel, comment: VideoComment, is_like: bool) -> dict:
        ...

    @abstractmethod
    def like_delete(self, channel: Channel, comment: VideoComment) -> int:
        ...

    @abstractmethod
    def update_like_status(self, like_id: int, is_like: bool) -> None:
        ...


class ORMVideoCommentRepository(BaseVideoCommentRepository):
    def get_all_comments(self) -> Iterable[VideoComment]:
        return VideoComment.objects.all()

    def change_comment_updated_status(self, comment_id: str) -> None:
        VideoComment.objects.filter(id=comment_id).update(is_updated=True)

    def get_by_id(self, id: str) -> VideoComment:
        return VideoComment.objects.filter(id=id).first()

    def like_get_or_create(self, channel: Channel, comment: VideoComment, is_like: bool) -> dict:
        like, created = VideoCommentLikeItem.objects.get_or_create(
            author=channel,
            comment=comment,
            defaults={'is_like': is_like},
        )
        return like, created

    def update_like_status(self, like_id: int, is_like: bool) -> None:
        VideoCommentLikeItem.objects.filter(id=like_id).update(is_like=is_like)

    def like_delete(self, channel: Channel, comment: VideoComment) -> int:
        deleted, _ = VideoCommentLikeItem.objects.filter(
            author=channel,
            comment=comment,
        ).delete()

        return deleted
