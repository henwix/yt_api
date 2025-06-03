from rest_framework.test import APIClient

import pytest
from punq import Container
from rest_framework_simplejwt.tokens import RefreshToken

from core.apps.channels.models import Channel
from core.apps.videos.models import Video
from core.project.containers import get_container
from core.tests.factories.channels import (
    ChannelModelFactory,
    UserModelFactory,
)
from core.tests.factories.videos import VideoModelFactory


@pytest.fixture
def container() -> Container:
    return get_container()


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
