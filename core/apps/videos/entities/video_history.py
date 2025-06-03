from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoHistoryEntity:
    id: str
    channel_id: str
    video_id: str
    watched_at: datetime
