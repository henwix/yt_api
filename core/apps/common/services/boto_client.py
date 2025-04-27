import os
from abc import (
    ABC,
    abstractmethod,
)
from typing import Any

from boto3 import client


class BaseBotoClientService(ABC):
    @abstractmethod
    def get_s3_client(self) -> Any:
        ...

    @abstractmethod
    def get_bucket_name(self) -> str:
        ...


class BotoClientService(BaseBotoClientService):
    def get_s3_client(self) -> Any:
        return client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME'),
        )

    def get_bucket_name(self) -> str:
        return os.environ.get('AWS_STORAGE_BUCKET_NAME')
