from dataclasses import (
    dataclass,
    field,
)

from core.apps.common.enums import EntityStatus
from core.apps.videos.entities.videos import VideoEntity


@dataclass
class PlaylistEntity:
    id: str
    channel_id: str
    videos: list[VideoEntity] | EntityStatus = field(default=EntityStatus.NOT_LOADED, kw_only=True)
    title: str
    description: str
    status: str


@dataclass
class PlaylistItemEntity:
    id: int
    playlist_id: str
    video_id: str
