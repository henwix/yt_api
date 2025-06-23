from core.apps.videos.entities.comments import VideoCommentEntity
from core.apps.videos.models import VideoComment


def video_comment_from_entity(video_comment: VideoCommentEntity) -> VideoComment:
    return VideoComment(
        pk=video_comment.id,
        text=video_comment.text,
        created_at=video_comment.created_at,
        is_updated=video_comment.is_updated,
        author_id=video_comment.author_id,
        video_id=video_comment.video_id,
        reply_comment_id=video_comment.reply_comment_id,
        reply_level=video_comment.reply_level,
    )


def video_comment_to_entity(video_comment: VideoComment) -> VideoCommentEntity:
    return VideoCommentEntity(
        id=video_comment.pk,
        text=video_comment.text,
        created_at=video_comment.created_at,
        is_updated=video_comment.is_updated,
        author_id=video_comment.author_id,
        video_id=video_comment.video_id,
        reply_comment_id=video_comment.reply_comment_id,
        reply_level=video_comment.reply_level,
    )
