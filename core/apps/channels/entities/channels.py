from dataclasses import (
    dataclass,
    field,
)


@dataclass
class ChannelEntity:
    id: int | None = field(default=None, kw_only=True)
    slug: str
    name: str
    description: str | None = field(default=None, kw_only=True)
    user_id: int
    country: str | None = None
    avatar_s3_key: str | None = None
