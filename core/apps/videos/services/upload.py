from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.videos.exceptions.upload import (
    FilenameNotProvidedError,
    UnsupportedFileFormatError,
    VideoWithUploadIdNotFoundError,
)
from core.apps.videos.models import Video


class BaseVideoS3UploadValidatorService(ABC):
    @abstractmethod
    def validate(self, video: Video | None, upload_id: str) -> None:
        ...


class VideoS3UploadExistsValidatorService(BaseVideoS3UploadValidatorService):
    def validate(self, video: Video | None, upload_id: str) -> None:
        if not video:
            raise VideoWithUploadIdNotFoundError(upload_id=upload_id)


class BaseFilenameValidatorService(ABC):
    @abstractmethod
    def validate(self, filename: str) -> None:
        ...


class FilenameExistsValidatorService(BaseFilenameValidatorService):
    def validate(self, filename: str) -> None:
        if filename is None:
            raise FilenameNotProvidedError()


class FilenameFormatValidatorService(BaseFilenameValidatorService):
    def validate(self, filename: str) -> None:
        if filename[-4:] not in ['.mkv', '.mp4']:
            raise UnsupportedFileFormatError(filename=filename)


@dataclass
class ComposedFilenameValidatorService(BaseFilenameValidatorService):
    validators: list[BaseFilenameValidatorService]

    def validate(self, filename: str) -> None:
        for validator in self.validators:
            validator.validate(filename=filename)
