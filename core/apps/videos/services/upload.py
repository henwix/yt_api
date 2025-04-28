from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.videos.exceptions.upload import (
    FilenameNotProvidedError,
    IncorrectVideoUploadIdError,
    KeyNotProvidedError,
    UnsupportedFileFormatError,
    UploadIdNotProvidedError,
)
from core.apps.videos.models import Video


class BaseVideoS3UploadValidatorService(ABC):
    @abstractmethod
    def validate(self, video: Video | None, upload_id: str) -> None:
        ...


class VideoS3UploadValidatorService(BaseVideoS3UploadValidatorService):
    def validate(self, video: Video | None, upload_id: str) -> None:
        if not video:
            raise IncorrectVideoUploadIdError(upload_id=upload_id)


class BaseUploadIdValidatorService(ABC):
    @abstractmethod
    def validate(self, upload_id: str) -> None:
        ...


class UploadIdExistsValidatorService(BaseUploadIdValidatorService):
    def validate(self, upload_id: str) -> None:
        if not upload_id:
            raise UploadIdNotProvidedError()


class BaseUploadKeyValidatorService(ABC):
    @abstractmethod
    def validate(self, key: str) -> None:
        ...


class UploadKeyExistsValidatorService(BaseUploadKeyValidatorService):
    def validate(self, key: str) -> None:
        if not key:
            raise KeyNotProvidedError()


class BaseUploadPartNumberValidatorService(ABC):
    @abstractmethod
    def validate(self, part_number: str) -> None:
        ...


class UploadPartNumberExistsValidatorService(BaseUploadPartNumberValidatorService):
    def validate(self, part_number: str) -> None:
        if not part_number:
            raise KeyNotProvidedError()


class BaseFilenameValidatorService(ABC):
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


# @abstractmethod
# def BaseUploadPartVli
