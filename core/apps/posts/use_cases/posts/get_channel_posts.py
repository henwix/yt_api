from dataclasses import dataclass
from typing import Iterable

from core.apps.posts.models import Post
from core.apps.posts.services.posts import BasePostService


@dataclass
class GetChannelPostsUseCase:
    service: BasePostService

    def execute(self, slug: str) -> Iterable[Post]:
        qs = self.service.get_related_posts_by_author_slug(slug=slug)
        return qs
