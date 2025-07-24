import punq
import pytest

from core.apps.posts.use_cases.posts_comments.create_comment import CreatePostCommentUseCase


@pytest.fixture
def create_post_comment_use_case(container: punq.Container) -> CreatePostCommentUseCase:
    return container.resolve(CreatePostCommentUseCase)
