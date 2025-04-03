import pytest
from punq import Container
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.apps.channels.models import Channel
from core.project.containers import get_container

from .factories.channels import ChannelModelFactory


@pytest.fixture
def container() -> Container:
    return get_container()


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def jwt_access() -> str:
    """Generates JWT token to API access"""

    channel = ChannelModelFactory()
    return f'Bearer {RefreshToken().for_user(channel.user).access_token}'


@pytest.fixture
def channel() -> Channel:
    return ChannelModelFactory()
