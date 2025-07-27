import punq
import pytest

from core.apps.posts.use_cases.posts_comments.create_comment import CreatePostCommentUseCase
from core.apps.posts.use_cases.posts_comments.get_list_comments import GetPostCommentsUseCase
from core.apps.posts.use_cases.posts_comments.get_replies_list_comments import GetPostCommentRepliesUseCase
from core.apps.posts.use_cases.posts_comments.like_create import PostCommentLikeCreateUseCase
from core.apps.posts.use_cases.posts_comments.like_delete import PostCommentLikeDeleteUseCase


@pytest.fixture
def create_post_comment_use_case(container: punq.Container) -> CreatePostCommentUseCase:
    return container.resolve(CreatePostCommentUseCase)


@pytest.fixture
def get_post_comments_use_case(container: punq.Container) -> GetPostCommentsUseCase:
    return container.resolve(GetPostCommentsUseCase)


@pytest.fixture
def get_post_comment_replies_use_case(container: punq.Container) -> GetPostCommentRepliesUseCase:
    return container.resolve(GetPostCommentRepliesUseCase)


@pytest.fixture
def post_comment_like_create_use_case(container: punq.Container) -> PostCommentLikeCreateUseCase:
    return container.resolve(PostCommentLikeCreateUseCase)


@pytest.fixture
def post_comment_like_delete_use_case(container: punq.Container) -> PostCommentLikeDeleteUseCase:
    return container.resolve(PostCommentLikeDeleteUseCase)
