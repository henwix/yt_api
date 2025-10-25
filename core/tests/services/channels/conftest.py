import pytest
from django.contrib.auth import get_user_model
from punq import Container

from core.apps.channels.services.channels import (
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
)
from core.apps.channels.services.s3_channels import (
    BaseAvatarFilenameValidatorService,
    BaseAvatarValidatorService,
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


@pytest.fixture
def avatar_validator_service(container: Container) -> BaseAvatarValidatorService:
    return container.resolve(BaseAvatarValidatorService)


@pytest.fixture
def avatar_filename_validator_service(container: Container) -> BaseAvatarFilenameValidatorService:
    return container.resolve(BaseAvatarFilenameValidatorService)
