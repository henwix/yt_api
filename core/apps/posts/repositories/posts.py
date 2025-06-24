from abc import (
    ABC,
    abstractmethod,
)

from core.apps.posts.converters.posts import post_to_entity
from core.apps.posts.entities.posts import PostEntity
from core.apps.posts.models import Post


class BasePostRepository(ABC):
    @abstractmethod
    def create_post(self, post_entity: PostEntity) -> PostEntity:
        ...


class PostRepository(BasePostRepository):
    def create_post(self, post_entity: PostEntity) -> PostEntity:
        post_dto = Post.objects.create(**post_entity.__dict__)
        return post_to_entity(post=post_dto)
