from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime


@dataclass
class UserEntity:
    id: int
    email: str
    username: str
    otp_enabled: bool
    is_staff: bool
    is_superuser: bool
    is_active: bool
    date_joined: datetime
    is_anonymous: bool = field(default=False, kw_only=True)


@dataclass
class AnonymousUserEntity:
    is_anonymous: bool = field(default=True, kw_only=True)
