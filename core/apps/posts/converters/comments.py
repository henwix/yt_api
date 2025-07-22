from core.apps.posts.entities.comments import PostCommentEntity
from core.apps.posts.models import PostCommentItem


def post_comment_from_entity(post_comment: PostCommentEntity) -> PostCommentItem:
    return PostCommentItem(
        pk=post_comment.id,
        text=post_comment.text,
        created_at=post_comment.created_at,
        is_updated=post_comment.is_updated,
        author_id=post_comment.author_id,
        post_id=post_comment.post_id,
        reply_comment_id=post_comment.reply_comment_id,
        reply_level=post_comment.reply_level,
    )


def post_comment_to_entity(post_comment: PostCommentItem) -> PostCommentEntity:
    return PostCommentEntity(
        id=post_comment.pk,
        text=post_comment.text,
        created_at=post_comment.created_at,
        is_updated=post_comment.is_updated,
        author_id=post_comment.author_id,
        post_id=post_comment.post_id,
        reply_comment_id=post_comment.reply_comment_id,
        reply_level=post_comment.reply_level,
    )


def data_to_post_comment_entity(data: dict) -> PostCommentEntity:
    return PostCommentEntity(**data)
