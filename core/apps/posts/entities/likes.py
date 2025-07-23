from dataclasses import dataclass


@dataclass
class PostLikeEntity:
    id: int
    channel_id: int
    post_id: str
    is_like: bool


@dataclass
class PostCommentLikeItemEntity:
    id: int
    author_id: int
    comment_id: int
    is_like: bool
