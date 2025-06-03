from dataclasses import dataclass


@dataclass
class VideoLikeEntity:
    id: int
    channel_id: int
    video_id: str
    is_like: bool


@dataclass
class VideoCommentLikeItemEntity:
    id: int
    author_id: int
    comment_id: str
    is_like: bool
