from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoCommentEntity:
    id: int
    text: str
    created_at: datetime
    is_updated: bool
    author_id: int
    video_id: str
    comment_id: int | None
    reply_level: int
    # likes
