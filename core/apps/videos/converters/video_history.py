from core.apps.videos.entities.video_history import VideoHistoryEntity
from core.apps.videos.models import VideoHistory


def video_history_from_entity(video_history: VideoHistoryEntity) -> VideoHistory:
    return VideoHistory(
        pk=video_history.id,
        channel_id=video_history.channel_id,
        video_id=video_history.video_id,
        watched_at=video_history.watched_at,
    )


def video_history_to_entity(video_history: VideoHistory) -> VideoHistoryEntity:
    return VideoHistoryEntity(
        id=video_history.pk,
        channel_id=video_history.channel_id,
        video_id=video_history.video_id,
        watched_at=video_history.watched_at,
    )
