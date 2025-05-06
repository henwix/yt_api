from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


class BaseCeleryFileProvider(ABC):
    @abstractmethod
    def delete_object_by_key(self, key: str, cache_key: str | None = None) -> None:
        ...

    @abstractmethod
    def delete_objects(self, objects: list[dict]) -> None:
        ...

    @abstractmethod
    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        ...


@dataclass
class BaseBotoFileProvider(ABC):
    @abstractmethod
    def create_multipart_upload(
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
    ) -> str:
        ...

    @abstractmethod
    def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: list,
    ) -> dict:
        ...

    @abstractmethod
    def delete_object_by_key(
        self,
        key: str,
    ) -> None:
        ...

    @abstractmethod
    def delete_objects(
        self,
        objects: list[dict],
    ) -> dict:
        ...

    @abstractmethod
    def generate_upload_url(
        self,
        filename: str,
        expires_in: int,
        data_type: str,
    ) -> tuple:
        ...

    @abstractmethod
    def head_object(
        self,
        key: str,
    ) -> None:
        """Check if object exists in S3 bucket.

        Args:
            key: The key of the object to check

        Raises:
            ClientError: If object does not exist or other S3 error occurs

        """
        ...
