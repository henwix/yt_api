from dataclasses import (
    dataclass,
    field,
)

from core.apps.common.enums import EntityStatus
from core.apps.users.entities import UserEntity


@dataclass
class ChannelEntity:
    id: int
    slug: str
    name: str
    description: str
    user_id: int
    user: UserEntity | EntityStatus = field(default=EntityStatus.NOT_LOADED, kw_only=True)
    country: str
    avatar_s3_key: str
