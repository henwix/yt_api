import punq

from core.apps.posts.repositories.posts import (
    BasePostRepository,
    PostRepository,
)
from core.apps.posts.services.posts import (
    BasePostAuthorSlugValidatorService,
    BasePostService,
    PostAuthorSlugValidatorService,
    PostService,
)
from core.apps.posts.use_cases.create_post import CreatePostUseCase
from core.apps.posts.use_cases.get_channel_posts import GetChannelPostsUseCase


def init_posts(container: punq.Container) -> None:
    # use cases
    container.register(CreatePostUseCase)
    container.register(GetChannelPostsUseCase)

    # services
    container.register(BasePostService, PostService)
    container.register(BasePostAuthorSlugValidatorService, PostAuthorSlugValidatorService)

    # repos
    container.register(BasePostRepository, PostRepository)
