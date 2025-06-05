from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from django.utils import timezone

from core.apps.videos.models import Video


@dataclass
class VideoEntity:
    id: str | None = field(default=None, kw_only=True)
    author_id: int
    name: str
    description: str | None = field(default=None, kw_only=True)
    created_at: datetime = field(default_factory=timezone.now, kw_only=True)
    upload_id: datetime | None
    s3_key: str | None = field(default=None, kw_only=True)
    status: str = field(default=Video.VideoStatus.PUBLIC, kw_only=True)
    upload_status: str = field(default=Video.UploadStatus.UPLOADING, kw_only=True)
    is_reported: bool = field(default=False, kw_only=True)

    reports_count: int = field(default=0, kw_only=True)
