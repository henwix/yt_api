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
from core.apps.posts.use_cases.create_post import PostCreateUseCase
from core.apps.posts.use_cases.create_post_like import PostLikeCreateUseCase
from core.apps.posts.use_cases.delete_post_like import PostLikeDeleteUseCase
from core.apps.posts.use_cases.get_channel_posts import GetChannelPostsUseCase


def init_posts(container: punq.Container) -> None:
    # use cases
    container.register(PostCreateUseCase)
    container.register(GetChannelPostsUseCase)

    container.register(PostLikeCreateUseCase)
    container.register(PostLikeDeleteUseCase)

    # services
    container.register(BasePostService, PostService)
    container.register(BasePostAuthorSlugValidatorService, PostAuthorSlugValidatorService)

    # repos
    container.register(BasePostRepository, PostRepository)
