from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.services.cache import BaseCacheService
from core.apps.videos.exceptions.upload import (
    FilenameNotProvidedError,
    UnsupportedFileFormatError,
    VideoNotFoundByUploadIdError,
)
from core.apps.videos.models import Video
from core.apps.videos.providers.videos import (
    BaseBotoFileProvider,
    BaseCeleryFileProvider,
)


class BaseVideoS3UploadValidatorService(ABC):
    @abstractmethod
    def validate(self, video: Video | None, upload_id: str) -> None:
        ...


class VideoS3UploadExistsValidatorService(BaseVideoS3UploadValidatorService):
    def validate(self, video: Video | None, upload_id: str) -> None:
        if not video:
            raise VideoNotFoundByUploadIdError(upload_id=upload_id)


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


@dataclass
class BaseS3FileService(ABC):
    @abstractmethod
    def init_multipart_upload(self, filename: str, content_type: str = 'video/mp4') -> tuple:
        ...

    @abstractmethod
    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        ...

    @abstractmethod
    def generate_upload_part_url(self, key: str, upload_id: str, part_number: int):
        ...

    @abstractmethod
    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        ...

    @abstractmethod
    def complete_multipart_upload(self, key: str, upload_id: str, parts: list) -> str:
        ...

    @abstractmethod
    def delete_object_by_key(self, key: str) -> None:
        ...


@dataclass
class S3FileService(BaseS3FileService):
    boto_provider: BaseBotoFileProvider
    celery_provider: BaseCeleryFileProvider
    cache_service: BaseCacheService

    def init_multipart_upload(self, filename: str, content_type: str = 'video/mp4') -> tuple:
        response = self.boto_provider.init_multipart_upload(
            filename=filename,
            content_type=content_type,
        )

        return response.get('UploadId'), response.get('Key')

    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        self.celery_provider.abort_multipart_upload(
            key=key,
            upload_id=upload_id,
        )

    def generate_upload_part_url(
        self,
        key: str,
        upload_id: str,
        part_number: int,
    ) -> str:
        # TODO: посмотреть, одинаковые ли url получаются при одинаковых параметрах и если да, то добавить кэширование
        url = self.boto_provider.generate_upload_part_url(
            key=key,
            upload_id=upload_id,
            part_number=part_number,
        )
        return url

    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        cache_key = f's3_video_url_{key}'

        cached_url = self.cache_service.get_cached_data(key=cache_key)

        if cached_url:
            return cached_url

        url = self.boto_provider.generate_download_url(
            key=key,
            expires_in=expires_in,
        )

        self.cache_service.cache_data(key=cache_key, data=url, timeout=expires_in)

        return url

    def complete_multipart_upload(self, key: str, upload_id: str, parts: list) -> dict:
        response = self.boto_provider.complete_multipart_upload(
            key=key,
            upload_id=upload_id,
            parts=parts,
        )
        return response

    def delete_object_by_key(self, key: str) -> None:
        self.celery_provider.delete_object_by_key(key=key)
