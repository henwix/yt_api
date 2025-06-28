from dataclasses import dataclass


@dataclass
class PostLikeEntity:
    id: int
    channel_id: int
    post_id: str
    is_like: bool
