from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.providers.files import (
    BaseBotoFileProvider,
    BaseCeleryFileProvider,
)
from core.apps.common.services.cache import BaseCacheService


@dataclass
class BaseS3FileService(ABC):
    @abstractmethod
    def init_multipart_upload(
        self,
        filename: str,
        data_type: str,
    ) -> tuple:
        ...

    @abstractmethod
    def abort_multipart_upload(
        self,
        key: str,
        upload_id: str,
    ) -> None:
        ...

    @abstractmethod
    def generate_upload_part_url(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        expires_in: int,
    ) -> str:
        ...

    @abstractmethod
    def generate_download_url(
        self,
        key: str,
        expires_in: int,
        cache_key: str,
    ) -> str:
        ...

    @abstractmethod
    def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: list,
    ) -> str:
        ...

    @abstractmethod
    def delete_object_by_key(
        self,
        key: str,
    ) -> None:
        ...

    @abstractmethod
    def generate_upload_url(
        self,
        filename: str,
        expires_in: int,
        data_type: str,
    ) -> str:
        ...


@dataclass
class S3FileService(BaseS3FileService):
    boto_provider: BaseBotoFileProvider
    celery_provider: BaseCeleryFileProvider
    cache_service: BaseCacheService

    def init_multipart_upload(
        self,
        filename: str,
        data_type: str,
    ) -> tuple:
        response = self.boto_provider.init_multipart_upload(
            filename=filename,
            data_type=data_type,
        )

        return response.get('UploadId'), response.get('Key')

    def abort_multipart_upload(
        self,
        key: str,
        upload_id: str,
    ) -> None:
        self.celery_provider.abort_multipart_upload(
            key=key,
            upload_id=upload_id,
        )

    def generate_upload_part_url(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        expires_in: int,
    ) -> str:
        url = self.boto_provider.generate_upload_part_url(
            key=key,
            upload_id=upload_id,
            part_number=part_number,
            expires_in=expires_in,
        )
        return url

    def generate_download_url(
        self,
        key: str,
        expires_in: int,
        cache_key: str,
    ) -> str:
        cached_url = self.cache_service.get_cached_data(key=cache_key)

        if cached_url:
            return cached_url

        url = self.boto_provider.generate_download_url(
            key=key,
            expires_in=expires_in,
        )

        self.cache_service.cache_data(key=cache_key, data=url, timeout=expires_in)

        return url

    def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: list,
    ) -> dict:
        response = self.boto_provider.complete_multipart_upload(
            key=key,
            upload_id=upload_id,
            parts=parts,
        )
        return response

    def delete_object_by_key(self, key: str) -> None:
        self.celery_provider.delete_object_by_key(key=key)

    def generate_upload_url(
        self,
        filename: str,
        expires_in: int,
        data_type: str,
    ) -> str:
        url = self.boto_provider.generate_upload_url(
            filename=filename,
            expires_in=expires_in,
            data_type=data_type,
        )

        return url
