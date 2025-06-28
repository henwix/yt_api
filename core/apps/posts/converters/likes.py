from core.apps.posts.entities.likes import PostLikeEntity
from core.apps.posts.models import PostLikeItem


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
