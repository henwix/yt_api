from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.services.boto_client import BaseBotoClientService


class BaseCeleryFileProvider(ABC):
    @abstractmethod
    def delete_file(self, key: str) -> None:
        ...

    @abstractmethod
    def delete_files(self, files: list) -> None:
        ...

    @abstractmethod
    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        ...


@dataclass
class BaseBotoFileProvider(ABC):
    boto_service: BaseBotoClientService

    @abstractmethod
    def init_multipart_upload(self, filename: str, content_type: str = 'video/mp4') -> tuple:
        ...

    @abstractmethod
    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        ...

    @abstractmethod
    def generate_upload_part_url(self, key: str, upload_id: str, part_number: int, expires_in: int = 120) -> str:
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
