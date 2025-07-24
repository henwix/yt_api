import punq
import pytest

from core.apps.posts.models import PostLikeItem
from core.apps.posts.use_cases.posts.create_post import PostCreateUseCase
from core.apps.posts.use_cases.posts.create_post_like import PostLikeCreateUseCase
from core.apps.posts.use_cases.posts.delete_post_like import PostLikeDeleteUseCase
from core.apps.posts.use_cases.posts.get_channel_posts import GetChannelPostsUseCase
from core.tests.factories.posts import PostLikeModelFactory


@pytest.fixture
def create_post_use_case(container: punq.Container) -> PostCreateUseCase:
    return container.resolve(PostCreateUseCase)


@pytest.fixture
def channel_posts_use_case(container: punq.Container) -> GetChannelPostsUseCase:
    return container.resolve(GetChannelPostsUseCase)


@pytest.fixture
def post_like_create_use_case(container: punq.Container) -> PostLikeCreateUseCase:
    return container.resolve(PostLikeCreateUseCase)


@pytest.fixture
def post_like_delete_use_case(container: punq.Container) -> PostLikeDeleteUseCase:
    return container.resolve(PostLikeDeleteUseCase)


@pytest.fixture
def post_like() -> PostLikeItem:
    return PostLikeModelFactory()
