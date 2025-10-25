from core.apps.videos.entities.videos import VideoEntity
from core.apps.videos.models import Video


def video_from_entity(video: VideoEntity) -> Video:
    return Video(
        pk=video.id,
        author_id=video.author_id,
        name=video.name,
        description=video.description,
        created_at=video.created_at,
        upload_id=video.upload_id,
        s3_key=video.s3_key,
        status=video.status,
        upload_status=video.upload_status,
        is_reported=video.is_reported,
    )


def video_to_entity(video: Video) -> VideoEntity:
    return VideoEntity(
        id=video.pk,
        author_id=video.author_id,
        name=video.name,
        description=video.description,
        created_at=video.created_at,
        upload_id=video.upload_id,
        s3_key=video.s3_key,
        status=video.status,
        upload_status=video.upload_status,
        is_reported=video.is_reported,
        reports_count=getattr(video, 'reports_count', 0),
    )


def data_to_video_entity(data: dict) -> VideoEntity:
    return VideoEntity(**data)
