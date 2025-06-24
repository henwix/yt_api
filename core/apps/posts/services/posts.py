from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.posts.entities.posts import PostEntity
from core.apps.posts.repositories.posts import BasePostRepository


@dataclass
class BasePostService(ABC):
    post_repository: BasePostRepository

    @abstractmethod
    def create_post(self, post_entity: PostEntity) -> PostEntity:
        ...


class PostService(BasePostService):
    def create_post(self, post_entity: PostEntity) -> PostEntity:
        return self.post_repository.create_post(post_entity=post_entity)
