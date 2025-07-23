from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.videos.converters.comments import video_comment_to_entity
from core.apps.videos.converters.likes import video_comment_like_item_to_entity
from core.apps.videos.entities.comments import VideoCommentEntity
from core.apps.videos.entities.likes import VideoCommentLikeItemEntity
from core.apps.videos.models import (
    VideoComment,
    VideoCommentLikeItem,
)


class BaseVideoCommentRepository(ABC):
    @abstractmethod
    def create_comment(self, comment_entity: VideoCommentEntity) -> VideoCommentEntity:
        ...

    @abstractmethod
    def get_all_comments(self) -> Iterable[VideoComment]:
        ...

    @abstractmethod
    def change_updated_status(self, comment_id: str, is_updated: bool) -> None:
        ...

    @abstractmethod
    def get_by_id_or_none(self, id: int) -> VideoCommentEntity | None:
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

    @abstractmethod
    def update_like_status(self, like_id: int, is_like: bool) -> None:
        ...


class ORMVideoCommentRepository(BaseVideoCommentRepository):
    def create_comment(self, comment_entity: VideoCommentEntity) -> VideoCommentEntity:
        # comment_dto = video_comment_from_entity(comment_entity).save()
        comment_dto = VideoComment.objects.create(**comment_entity.__dict__)
        return video_comment_to_entity(comment_dto)

    def get_all_comments(self) -> Iterable[VideoComment]:
        return VideoComment.objects.all()

    def change_updated_status(self, comment_id: str, is_updated: bool) -> None:
        VideoComment.objects.filter(id=comment_id).update(is_updated=is_updated)

    def get_by_id_or_none(self, id: int) -> VideoCommentEntity | None:
        comment_dto = VideoComment.objects.filter(id=id).first()
        return video_comment_to_entity(comment_dto) if comment_dto else None

    def like_get_or_create(
        self,
        author: ChannelEntity,
        comment: VideoCommentEntity,
        is_like: bool,
    ) -> tuple[VideoCommentLikeItemEntity, bool]:
        like_dto, created = VideoCommentLikeItem.objects.get_or_create(
            author_id=author.id,
            comment_id=comment.id,
            defaults={'is_like': is_like},
        )
        return video_comment_like_item_to_entity(like_dto), created

    def update_like_status(self, like_id: int, is_like: bool) -> None:
        VideoCommentLikeItem.objects.filter(id=like_id).update(is_like=is_like)

    def like_delete(self, author: ChannelEntity, comment: VideoCommentEntity) -> bool:
        deleted, _ = VideoCommentLikeItem.objects.filter(
            author_id=author.id,
            comment_id=comment.id,
        ).delete()

        return True if deleted else False
