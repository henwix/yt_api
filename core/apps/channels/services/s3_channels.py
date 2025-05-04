from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from django.contrib.auth import get_user_model

from core.apps.channels.exceptions.channels import AvatarDoesNotExistsError
from core.apps.channels.exceptions.upload import (
    AvatarFilenameFormatError,
    AvatarFilenameNotProvidedError,
)
from core.apps.channels.models import Channel


User = get_user_model()


class BaseAvatarValidatorService(ABC):
    @abstractmethod
    def validate(self, channel: Channel) -> None:
        ...


class AvatarExistsValidatorService(BaseAvatarValidatorService):
    def validate(self, channel: Channel) -> None:
        if channel.avatar_s3_key is None:
            raise AvatarDoesNotExistsError(channel_slug=channel.slug)


@dataclass
class BaseAvatarFilenameValidatorService(ABC):
    @abstractmethod
    def validate(self, filename: str) -> None:
        ...


class AvatarFilenameExistsValidatorService(BaseAvatarFilenameValidatorService):
    def validate(self, filename: str) -> None:
        if filename is None:
            raise AvatarFilenameNotProvidedError()


class AvatarFilenameFormatValidatorService(BaseAvatarFilenameValidatorService):
    def validate(self, filename: str) -> None:
        if filename[-4:] not in ['.png', '.jpg', '.jpeg']:
            raise AvatarFilenameFormatError(filename=filename)


# TODO: add validator for avatar size
@dataclass
class ComposedAvatarFilenameValidatorService(BaseAvatarFilenameValidatorService):
    validators: list[BaseAvatarFilenameValidatorService]

    def validate(self, filename: str) -> None:
        for validator in self.validators:
            validator.validate(filename=filename)
