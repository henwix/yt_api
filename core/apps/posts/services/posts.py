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

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.posts.entities.likes import PostLikeEntity
from core.apps.posts.entities.posts import PostEntity
from core.apps.posts.exceptions import (
    PostAuthorSlugNotProvidedError,
    PostNotFoundError,
)
from core.apps.posts.models import Post
from core.apps.posts.repositories.posts import BasePostRepository


class BasePostAuthorSlugValidatorService(ABC):
    @abstractmethod
    def validate(self, slug: str | None) -> None:
        ...


class PostAuthorSlugValidatorService(BasePostAuthorSlugValidatorService):
    def validate(self, slug: str | None) -> None:
        if not slug:
            raise PostAuthorSlugNotProvidedError()


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

    @abstractmethod
    def get_related_posts_by_author_slug(self, slug: str | None) -> Iterable[Post]:
        ...

    @abstractmethod
    def get_post_by_id_or_404(self, post_id: str) -> PostEntity:
        ...

    @abstractmethod
    def like_get_or_create(
        self,
        channel: ChannelEntity,
        post: PostEntity,
        is_like: bool,
    ) -> tuple[PostLikeEntity, bool]:
        ...

    @abstractmethod
    def like_delete(self, channel: ChannelEntity, post: PostEntity) -> bool:
        ...

    @abstractmethod
    def update_is_like_field(self, like: PostLikeEntity, is_like: bool) -> None:
        ...


class PostService(BasePostService):
    def _build_query_with_related_fields_and_annotations(self, query: Iterable[Post]) -> Iterable[Post]:
        """Load the related 'author' field and add 'likes_count' and
        'comments_count' as annotations."""

        return query.select_related('author').annotate(
            likes_count=Count('likes', distinct=True, filter=Q(likes_items__is_like=True)),
            comments_count=Count('comments_items', distinct=True),
        )

    def create_post(self, post_entity: PostEntity) -> PostEntity:
        """Create new Post instance."""

        return self.post_repository.create_post(post_entity=post_entity)

    def get_all_posts(self) -> Iterable[Post]:
        """Return all instances from Post model."""

        return self.post_repository.get_all_posts()

    def get_posts_for_retrieving(self) -> Iterable[Post]:
        """Return all Post instances for retrieving, using
        '_build_query_with_related_fields_and_annotations' method."""

        qs = self.post_repository.get_all_posts()
        return self._build_query_with_related_fields_and_annotations(query=qs)

    def get_related_posts_by_author_slug(self, slug: str | None) -> Iterable[Post]:
        """Return instances sorted by author 'slug', using
        '_build_query_with_related_fields_and_annotations' method."""

        qs = self._build_query_with_related_fields_and_annotations(
            query=self.post_repository.get_all_posts(),
        )
        return qs.filter(author__slug=slug)

    def get_post_by_id_or_404(self, post_id: str) -> PostEntity:
        post = self.post_repository.get_post_by_id(post_id=post_id)

        if not post:
            raise PostNotFoundError(post_id=post_id)
        return post

    def like_get_or_create(
        self,
        channel: ChannelEntity,
        post: PostEntity,
        is_like: bool,
    ) -> tuple[PostLikeEntity, bool]:
        return self.post_repository.like_get_or_create(
            channel=channel,
            post=post,
            is_like=is_like,
        )

    def like_delete(self, channel: ChannelEntity, post: PostEntity) -> bool:
        return self.post_repository.like_delete(
            channel=channel,
            post=post,
        )

    def update_is_like_field(self, like: PostLikeEntity, is_like: bool) -> None:
        self.post_repository.update_is_like_field(
            like=like,
            is_like=is_like,
        )
