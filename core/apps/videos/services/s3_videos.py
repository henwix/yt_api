from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.videos.exceptions.upload import (
    VideoFilenameNotProvidedError,
    VideoFilenameNotSupportedFormatError,
)


class BaseVideoFilenameValidatorService(ABC):
    @abstractmethod
    def validate(self, filename: str | None) -> None: ...


class VideoFilenameExistsValidatorService(BaseVideoFilenameValidatorService):
    def validate(self, filename: str | None) -> None:
        if filename is None:
            raise VideoFilenameNotProvidedError()


class VideoFilenameFormatValidatorService(BaseVideoFilenameValidatorService):
    def validate(self, filename: str) -> None:
        if filename[-4:] not in ['.mkv', '.mp4']:
            raise VideoFilenameNotSupportedFormatError(filename=filename)


@dataclass
class ComposedVideoFilenameValidatorService(BaseVideoFilenameValidatorService):
    validators: list[BaseVideoFilenameValidatorService]

    def validate(self, filename: str) -> None:
        for validator in self.validators:
            validator.validate(filename=filename)
