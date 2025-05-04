from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.videos.exceptions.upload import (
    VideoFilenameFormatError,
    VideoFilenameNotProvidedError,
    VideoNotFoundByUploadIdError,
)
from core.apps.videos.models import Video


class BaseUploadVideoValidatorService(ABC):
    @abstractmethod
    def validate(self, video: Video | None, upload_id: str) -> None:
        ...


class UploadVideoExistsValidatorService(BaseUploadVideoValidatorService):
    def validate(self, video: Video | None, upload_id: str) -> None:
        if not video:
            raise VideoNotFoundByUploadIdError(upload_id=upload_id)


class BaseVideoFilenameValidatorService(ABC):
    @abstractmethod
    def validate(self, filename: str) -> None:
        ...


class VideoFilenameExistsValidatorService(BaseVideoFilenameValidatorService):
    def validate(self, filename: str) -> None:
        if filename is None:
            raise VideoFilenameNotProvidedError()


class VideoFilenameFormatValidatorService(BaseVideoFilenameValidatorService):
    def validate(self, filename: str) -> None:
        if filename[-4:] not in ['.mkv', '.mp4']:
            raise VideoFilenameFormatError(filename=filename)


@dataclass
class ComposedVideoFilenameValidatorService(BaseVideoFilenameValidatorService):
    validators: list[BaseVideoFilenameValidatorService]

    def validate(self, filename: str) -> None:
        for validator in self.validators:
            validator.validate(filename=filename)
