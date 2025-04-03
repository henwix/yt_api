import pytest
from django.contrib.auth.models import User
from punq import Container

from core.apps.channels.models import Channel
from core.apps.channels.services.channels import BaseChannelService, BaseChannelSubsService, BaseSubscriptionService
from core.tests.factories.channels import ChannelModelFactory


@pytest.fixture
def channel_service(container: Container) -> BaseChannelService:
    return container.resolve(BaseChannelService)


@pytest.fixture
def channel_sub_service(container: Container) -> BaseChannelSubsService:
    return container.resolve(BaseChannelSubsService)


@pytest.fixture
def subscription_service(container: Container) -> BaseSubscriptionService:
    return container.resolve(BaseSubscriptionService)


@pytest.fixture
def user_with_channel() -> User:
    channel = ChannelModelFactory()
    return channel.user


@pytest.fixture
def channel() -> Channel:
    return ChannelModelFactory()
