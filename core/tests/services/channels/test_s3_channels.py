import pytest

from core.apps.channels.exceptions.channels import AvatarDoesNotExistsError
from core.apps.channels.exceptions.upload import (
    AvatarFilenameFormatError,
    AvatarFilenameNotProvidedError,
)
from core.apps.channels.models import Channel
from core.apps.channels.services.s3_channels import (
    BaseAvatarFilenameValidatorService,
    BaseAvatarValidatorService,
)
from core.tests.factories.channels import ChannelModelFactory


@pytest.mark.django_db
def test_avatar_not_exists_error(avatar_validator_service: BaseAvatarValidatorService, channel: Channel):
    """Test error raised when avatar does not exist."""
    with pytest.raises(AvatarDoesNotExistsError):
        avatar_validator_service.validate(channel=channel)


@pytest.mark.django_db
def test_avatar_exists(avatar_validator_service: BaseAvatarValidatorService):
    """Test avatar exists."""
    channel = ChannelModelFactory(avatar_s3_key='test.png')
    avatar_validator_service.validate(channel=channel)


@pytest.mark.django_db
def test_avatar_filename_not_provided_error(avatar_filename_validator_service: BaseAvatarFilenameValidatorService):
    """Test error raised when avatar filename is not provided."""
    with pytest.raises(AvatarFilenameNotProvidedError):
        avatar_filename_validator_service.validate(filename=None)


@pytest.mark.django_db
def test_avatar_filename_format_error(avatar_filename_validator_service: BaseAvatarFilenameValidatorService):
    """Test error raised when avatar filename format is incorrect."""
    with pytest.raises(AvatarFilenameFormatError):
        avatar_filename_validator_service.validate(filename='test.txt')


@pytest.mark.django_db
@pytest.mark.parametrize('filename', ['test.png', 'test.jpg'])
def test_avatar_filename_format_correct(
    avatar_filename_validator_service: BaseAvatarFilenameValidatorService,
    filename: str,
):
    """Test avatar filename format is correct."""
    avatar_filename_validator_service.validate(filename=filename)
