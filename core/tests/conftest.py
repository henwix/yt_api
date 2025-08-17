from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

import punq
import pytest
from punq import Container
from rest_framework_simplejwt.tokens import RefreshToken

from core.apps.channels.models import Channel
from core.apps.posts.models import (
    Post,
    PostCommentItem,
)
from core.apps.users.providers.senders import BaseSenderProvider
from core.apps.users.services.codes import BaseCodeService
from core.apps.videos.models import Video
from core.project.containers import get_container
from core.tests.factories.channels import (
    ChannelModelFactory,
    UserModelFactory,
)
from core.tests.factories.posts import (
    PostCommentModelFactory,
    PostModelFactory,
)
from core.tests.factories.videos import VideoModelFactory
from core.tests.mocks.auth.email_provider import DummySenderProvider


User = get_user_model()


@pytest.fixture
def container() -> Container:
    return get_container()


@pytest.fixture
def mock_container() -> Container:
    container: punq.Container = get_container()

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
