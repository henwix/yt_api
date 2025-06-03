from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoReportEntity:
    id: int
    video_id: str
    author_id: int
    reason: str
    description: str
    created_at: datetime
