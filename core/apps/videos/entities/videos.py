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
    s3_key: str | None = field(default=None)
    status: str = field(default=Video.VideoStatus.PUBLIC)
    upload_status: str = field(default=Video.UploadStatus.UPLOADING)
    is_reported: bool = field(default=False)
