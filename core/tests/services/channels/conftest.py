import pytest
from apps.channels.services.channels import BaseChannelService
from django.contrib.auth.models import User
from punq import Container

from tests.factories.channels import ChannelModelFactory


@pytest.fixture
def channel_service(container: Container) -> BaseChannelService:
    return container.resolve(BaseChannelService)


@pytest.fixture
def user_with_channel() -> User:
    channel = ChannelModelFactory()
    return channel.user
