import punq
import pytest
from django.core.cache import cache
from punq import Container
from pytest_django.fixtures import SettingsWrapper
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.apps.channels.models import Channel
from core.apps.common.providers.senders import BaseSenderProvider
from core.apps.common.services.encoding import BaseEncodingService
from core.apps.payments.enums import StripeSubscriptionStatusesEnum
from core.apps.payments.providers.stripe_provider import BaseStripeProvider
from core.apps.payments.services.stripe_service import BaseStripeService
from core.apps.posts.models import (
    Post,
    PostCommentItem,
)
from core.apps.users.models import CustomUser
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
from core.tests.mocks.payments.stripe import DummyStripeProvider


@pytest.fixture(autouse=True)
def change_redis_database_number_and_clear_cache(settings: SettingsWrapper):
    """Change Redis database number and clear the cache before each test to avoid unpredictable caching
    behavior.
    Cache settings can also be changed using the new Django settings file in pyproject.toml instead of using fixture,
    but you won't be able to clear the cache before each test run"""
    settings.CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://redis:6379/8',
        },
    }
    cache.clear()


@pytest.fixture(autouse=True)
def disable_silk_middleware(settings: SettingsWrapper):
    """Fixture to disable Silk middleware when DEBUG == True.

    If it's enabled, it may impact test results.

    Can also be changed using the new Django settings file in pyproject.toml instead of using fixture

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

    container.register(BaseStripeProvider, DummyStripeProvider)
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
def user() -> CustomUser:
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


@pytest.fixture
def stripe_service(container: punq.Container) -> BaseStripeService:
    return container.resolve(BaseStripeService)


@pytest.fixture
def dummy_stripe_sub_object(request) -> dict:
    params = getattr(request, 'param', {})

    return {
        'id': params.get('id', 'sub_123456789'),
        'status': params.get('status', StripeSubscriptionStatusesEnum.ACTIVE),
        'cancel_at_period_end': params.get('cancel_at_period_end', False),
        'default_payment_method': params.get('default_payment_method', '123'),
        'items': {
            'data': [
                {
                    'price': {
                        'id': params.get('price_id', 'price_123456789'),
                    },
                    'current_period_start': params.get('current_period_start', 1762366397),
                    'current_period_end': params.get('current_period_end', 1764958397),
                },
            ],
        },
    }
