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
from core.apps.posts.use_cases.posts.create_post import PostCreateUseCase
from core.apps.posts.use_cases.posts.create_post_like import PostLikeCreateUseCase
from core.apps.posts.use_cases.posts.delete_post_like import PostLikeDeleteUseCase
from core.apps.posts.use_cases.posts.get_channel_posts import GetChannelPostsUseCase
from core.apps.posts.use_cases.posts_comments.create_comment import CreatePostCommentUseCase
from core.apps.posts.use_cases.posts_comments.get_list_comments import GetPostCommentsUseCase
from core.apps.posts.use_cases.posts_comments.get_replies_list_comments import GetPostCommentRepliesUseCase
from core.apps.posts.use_cases.posts_comments.like_create import PostCommentLikeCreateUseCase
from core.apps.posts.use_cases.posts_comments.like_delete import PostCommentLikeDeleteUseCase


def init_posts(container: punq.Container) -> None:
    # use cases
    container.register(PostCreateUseCase)
    container.register(GetChannelPostsUseCase)

    container.register(PostLikeCreateUseCase)
    container.register(PostLikeDeleteUseCase)

    container.register(CreatePostCommentUseCase)
    container.register(GetPostCommentsUseCase)
    container.register(GetPostCommentRepliesUseCase)
    container.register(PostCommentLikeCreateUseCase)
    container.register(PostCommentLikeDeleteUseCase)

    # services
    container.register(BasePostService, PostService)
    container.register(BasePostAuthorSlugValidatorService, PostAuthorSlugValidatorService)
    container.register(BasePostCommentService, PostCommentService)

    # repos
    container.register(BasePostRepository, PostRepository)
    container.register(BasePostCommentRepository, PostCommentRepository)
