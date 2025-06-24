import punq

from core.apps.posts.repositories.posts import (
    BasePostRepository,
    PostRepository,
)
from core.apps.posts.services.posts import (
    BasePostService,
    PostService,
)
from core.apps.posts.use_cases.create_post import CreatePostUseCase


def init_posts(container: punq.Container) -> None:
    # use cases
    container.register(CreatePostUseCase)

    # services
    container.register(BasePostService, PostService)

    # repos
    container.register(BasePostRepository, PostRepository)
