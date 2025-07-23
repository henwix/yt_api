from core.apps.posts.entities.likes import (
    PostCommentLikeItemEntity,
    PostLikeEntity,
)
from core.apps.posts.models import (
    PostCommentLikeItem,
    PostLikeItem,
)


def post_like_from_entity(like: PostLikeEntity) -> PostLikeItem:
    return PostLikeItem(
        pk=like.id,
        channel_id=like.channel_id,
        post_id=like.post_id,
        is_like=like.is_like,
    )


def post_like_to_entity(like: PostLikeItem) -> PostLikeEntity:
    return PostLikeEntity(
        id=like.pk,
        channel_id=like.channel_id,
        post_id=like.post_id,
        is_like=like.is_like,
    )


def post_comment_like_item_from_entity(like: PostCommentLikeItemEntity) -> PostCommentLikeItem:
    return PostCommentLikeItem(
        pk=like.id,
        author_id=like.author_id,
        comment_id=like.comment_id,
        is_like=like.is_like,
    )


def post_comment_like_item_to_entity(like: PostCommentLikeItem) -> PostCommentLikeItemEntity:
    return PostCommentLikeItemEntity(
        id=like.pk,
        author_id=like.author_id,
        comment_id=like.comment_id,
        is_like=like.is_like,
    )
