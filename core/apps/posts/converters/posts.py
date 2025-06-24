from core.apps.posts.entities.posts import PostEntity
from core.apps.posts.models import Post


def post_to_entity(post: Post) -> PostEntity:
    return PostEntity(
        pk=post.pk,
        author_id=post.author_id,
        text=post.text,
        created_at=post.created_at,
    )


def post_from_entity(post: PostEntity) -> Post:
    return Post(
        pk=post.pk,
        author_id=post.author_id,
        text=post.text,
        created_at=post.created_at,
    )


def data_to_post_entity(data: dict) -> PostEntity:
    return PostEntity(**data)
