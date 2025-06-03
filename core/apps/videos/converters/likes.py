from core.apps.videos.entities.likes import (
    VideoCommentLikeItemEntity,
    VideoLikeEntity,
)
from core.apps.videos.models import (
    VideoCommentLikeItem,
    VideoLike,
)


def video_like_from_entity(like: VideoLikeEntity) -> VideoLike:
    return VideoLike(
        pk=like.id,
        channel_id=like.channel_id,
        video_id=like.video_id,
        is_like=like.is_like,
    )


def video_like_to_entity(like: VideoLike) -> VideoLikeEntity:
    return VideoLikeEntity(
        id=like.id,
        channel_id=like.channel_id,
        video_id=like.video_id,
        is_like=like.is_like,
    )


def video_comment_like_item_from_entity(like: VideoCommentLikeItemEntity) -> VideoCommentLikeItem:
    return VideoCommentLikeItem(
        pk=like.id,
        author_id=like.author_id,
        comment_id=like.comment_id,
        is_like=like.is_like,
    )


def video_comment_like_item_to_entity(like: VideoCommentLikeItem) -> VideoCommentLikeItemEntity:
    return VideoCommentLikeItemEntity(
        id=like.pk,
        author_id=like.author_id,
        comment_id=like.comment_id,
        is_like=like.is_like,
    )
