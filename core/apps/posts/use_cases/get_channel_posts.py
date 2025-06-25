from dataclasses import dataclass
from typing import Iterable

from core.apps.posts.models import Post
from core.apps.posts.services.posts import (
    BasePostAuthorSlugValidatorService,
    BasePostService,
)


@dataclass
class GetChannelPostsUseCase:
    service: BasePostService
    validator_service: BasePostAuthorSlugValidatorService

    def execute(self, slug: str) -> Iterable[Post]:
        self.validator_service.validate(slug=slug)

        qs = self.service.get_related_posts_by_author_slug(slug=slug)
        return qs
