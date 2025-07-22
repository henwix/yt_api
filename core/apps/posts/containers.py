import punq

from core.apps.posts.repositories.comments import (
    BasePostCommentRepository,
    PostCommentRepository,
)
from core.apps.posts.repositories.posts import (
    BasePostRepository,
    PostRepository,
)
from core.apps.posts.services.comments import (
    BasePostCommentService,
    PostCommentService,
)
from core.apps.posts.services.posts import (
    BasePostAuthorSlugValidatorService,
    BasePostService,
    PostAuthorSlugValidatorService,
    PostService,
)
from core.apps.posts.use_cases.create_comment import CreatePostCommentUseCase
from core.apps.posts.use_cases.create_post import PostCreateUseCase
from core.apps.posts.use_cases.create_post_like import PostLikeCreateUseCase
from core.apps.posts.use_cases.delete_post_like import PostLikeDeleteUseCase
from core.apps.posts.use_cases.get_channel_posts import GetChannelPostsUseCase
from core.apps.posts.use_cases.get_list_comments import GetPostCommentsUseCase


def init_posts(container: punq.Container) -> None:
    # use cases
    container.register(PostCreateUseCase)
    container.register(GetChannelPostsUseCase)

    container.register(PostLikeCreateUseCase)
    container.register(PostLikeDeleteUseCase)

    container.register(CreatePostCommentUseCase)
    container.register(GetPostCommentsUseCase)

    # services
    container.register(BasePostService, PostService)
    container.register(BasePostAuthorSlugValidatorService, PostAuthorSlugValidatorService)
    container.register(BasePostCommentService, PostCommentService)

    # repos
    container.register(BasePostRepository, PostRepository)
    container.register(BasePostCommentRepository, PostCommentRepository)
