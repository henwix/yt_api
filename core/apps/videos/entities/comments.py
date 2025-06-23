from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from django.utils import timezone


@dataclass
class VideoCommentEntity:
    id: int | None = field(default=None, kw_only=True)
    text: str
    created_at: datetime = field(default_factory=timezone.now, kw_only=True)
    is_updated: bool = field(default=False, kw_only=True)
    author_id: int
    video_id: str
    reply_comment_id: int | None = field(default=None, kw_only=True)
    reply_level: int = field(default=0, kw_only=True)
    # likes

    def update_reply_level(self) -> int:
        """Update the 'reply_level' field based on the 'reply_comment_id'
        field."""

        if self.reply_comment_id is not None:
            self.reply_level = 1

        return self.reply_level
