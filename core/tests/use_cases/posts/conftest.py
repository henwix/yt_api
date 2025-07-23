import punq
import pytest

from core.apps.posts.use_cases.posts.create_post import PostCreateUseCase
from core.apps.posts.use_cases.posts.get_channel_posts import GetChannelPostsUseCase


@pytest.fixture
def create_post_use_case(container: punq.Container) -> PostCreateUseCase:
    return container.resolve(PostCreateUseCase)


@pytest.fixture
def get_channel_posts_use_case(container: punq.Container) -> GetChannelPostsUseCase:
    return container.resolve(GetChannelPostsUseCase)
