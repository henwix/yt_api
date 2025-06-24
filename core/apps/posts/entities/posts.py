import datetime
from dataclasses import (
    dataclass,
    field,
)

from django.utils import timezone


@dataclass
class PostEntity:
    pk: str | None = field(default=None, kw_only=True)
    author_id: int
    text: str
    created_at: datetime = field(default_factory=timezone.now)
