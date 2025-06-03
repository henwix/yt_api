from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.channels.exceptions.channels import AvatarDoesNotExistsError
from core.apps.channels.exceptions.upload import (
    AvatarFilenameFormatError,
    AvatarFilenameNotProvidedError,
)


class BaseAvatarValidatorService(ABC):
    @abstractmethod
    def validate(self, channel: ChannelEntity) -> None:
        ...


class AvatarExistsValidatorService(BaseAvatarValidatorService):
    def validate(self, channel: ChannelEntity) -> None:
        if not channel.avatar_s3_key or channel.avatar_s3_key is None:
            raise AvatarDoesNotExistsError(channel_slug=channel.slug)


@dataclass
class BaseAvatarFilenameValidatorService(ABC):
    @abstractmethod
    def validate(self, filename: str) -> None:
        ...


class AvatarFilenameExistsValidatorService(BaseAvatarFilenameValidatorService):
    def validate(self, filename: str | None) -> None:
        if filename is None:
            raise AvatarFilenameNotProvidedError()


class AvatarFilenameFormatValidatorService(BaseAvatarFilenameValidatorService):
    def validate(self, filename: str) -> None:
        if filename[-4:] not in ['.png', '.jpg']:
            raise AvatarFilenameFormatError(filename=filename)


@dataclass
class ComposedAvatarFilenameValidatorService(BaseAvatarFilenameValidatorService):
    validators: list[BaseAvatarFilenameValidatorService]

    def validate(self, filename: str) -> None:
        for validator in self.validators:
            validator.validate(filename=filename)
