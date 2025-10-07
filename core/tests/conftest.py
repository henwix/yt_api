from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

import punq
import pytest
from punq import Container
from pytest_django.fixtures import SettingsWrapper
from rest_framework_simplejwt.tokens import RefreshToken

from core.apps.channels.models import Channel
from core.apps.common.providers.senders import BaseSenderProvider
from core.apps.common.services.encoding import BaseEncodingService
from core.apps.posts.models import (
    Post,
    PostCommentItem,
)
from core.apps.users.services.codes import BaseCodeService
from core.apps.videos.models import Video
from core.project.containers import (
    _initialize_container,
    get_container,
)
from core.tests.factories.channels import (
    ChannelModelFactory,
    UserModelFactory,
)
from core.tests.factories.posts import (
    PostCommentModelFactory,
    PostModelFactory,
)
from core.tests.factories.videos import VideoModelFactory
from core.tests.mocks.common.providers.senders import DummySenderProvider


User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test to avoid unpredictable caching
    behavior."""
    cache.clear()


@pytest.fixture(autouse=True)
def disable_silk_middleware(settings: SettingsWrapper):
    """Fixture to disable Silk middleware when DEBUG == True.

    If it's enabled, it may impact test results

    """
    silk_middleware = 'silk.middleware.SilkyMiddleware'

    if silk_middleware in settings.MIDDLEWARE:
        settings.MIDDLEWARE = [i for i in settings.MIDDLEWARE if i != silk_middleware]


@pytest.fixture
def container() -> Container:
    return get_container()


@pytest.fixture
def mock_container() -> Container:
    """If we override something with mocks, it may affect the non-mock
    container and lead to unpredictable results.

    For this reason, we create a separate container object for mocks and
    use it without touching the main one. If we use 'get_container', it
    returns the cached container (singleton), whereas 'init_container'
    creates a new one.

    """
    container: punq.Container = _initialize_container()

    container.register(BaseSenderProvider, DummySenderProvider)

    return container


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def jwt() -> str:
    """Generates JWT token to API access."""

    channel = ChannelModelFactory()
    return f'Bearer {RefreshToken().for_user(channel.user).access_token}'


@pytest.fixture
def jwt_and_channel() -> tuple:
    """Generates JWT token to API access and returns channel."""

    channel = ChannelModelFactory()
    return f'Bearer {RefreshToken().for_user(channel.user).access_token}', channel


@pytest.fixture
def jwt_and_user() -> tuple:
    """Generates JWT token to API access and returns user."""

    user = UserModelFactory()
    return f'Bearer {RefreshToken().for_user(user).access_token}', user


@pytest.fixture
def channel() -> Channel:
    """Returns channel object."""
    return ChannelModelFactory()


@pytest.fixture
def video() -> Video:
    """Returns video object."""
    return VideoModelFactory()


@pytest.fixture
def user() -> User:
    return UserModelFactory()


@pytest.fixture
def post() -> Post:
    return PostModelFactory()


@pytest.fixture
def post_comment() -> PostCommentItem:
    return PostCommentModelFactory()


@pytest.fixture
def code_service(container: punq.Container) -> BaseCodeService:
    return container.resolve(BaseCodeService)


@pytest.fixture
def encoding_service(container: punq.Container) -> BaseEncodingService:
    return container.resolve(BaseEncodingService)
