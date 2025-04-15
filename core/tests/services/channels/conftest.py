from django.contrib.auth import get_user_model

import pytest
from punq import Container

from core.apps.channels.services.channels import (
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
)
from core.tests.factories.channels import ChannelModelFactory


User = get_user_model()


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
def channel_main_service(container: Container) -> BaseChannelMainService:
    return container.resolve(BaseChannelMainService)


@pytest.fixture
def user_with_channel() -> User:
    channel = ChannelModelFactory()
    return channel.user
