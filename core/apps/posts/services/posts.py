from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from django.db.models import (
    Count,
    Q,
)

from core.apps.posts.entities.posts import PostEntity
from core.apps.posts.models import Post
from core.apps.posts.repositories.posts import BasePostRepository


@dataclass
class BasePostService(ABC):
    post_repository: BasePostRepository

    @abstractmethod
    def create_post(self, post_entity: PostEntity) -> PostEntity:
        ...

    @abstractmethod
    def get_all_posts(self) -> Iterable[Post]:
        ...

    @abstractmethod
    def get_posts_for_retrieving(self) -> Iterable[Post]:
        ...


class PostService(BasePostService):
    def create_post(self, post_entity: PostEntity) -> PostEntity:
        return self.post_repository.create_post(post_entity=post_entity)

    def get_all_posts(self) -> Iterable[Post]:
        """Return all objects from Post model."""
        return self.post_repository.get_all_posts()

    def get_posts_for_retrieving(self) -> Iterable[Post]:
        """Load 'author' related field, add the 'likes_count' and the
        'comments_count' as annotations."""
        qs = self.post_repository.get_all_posts()

        return qs.select_related('author').annotate(
            likes_count=Count('likes', distinct=True, filter=Q(likes_items__is_like=True)),
            comments_count=Count('comments', distinct=True),
        )
