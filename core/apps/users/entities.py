from dataclasses import (
    dataclass,
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
    is_anonymous: bool = False


@dataclass
class AnonymousUserEntity:
    id: None = None
    pk: None = None
    username: str = ''
    is_staff: bool = False
    is_superuser: bool = False
    is_active: bool = False
    is_anonymous: bool = True
