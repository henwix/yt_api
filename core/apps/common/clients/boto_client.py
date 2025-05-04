import os
from dataclasses import (
    dataclass,
    field,
)
from typing import Any

from boto3 import client


@dataclass
class BotoClient:
    key_prefixes: dict = field(
        default_factory=lambda: {
            'video': os.environ.get('AWS_S3_VIDEO_BUCKET_PREFIX'),
            'avatar': os.environ.get('AWS_S3_AVATAR_BUCKET_PREFIX'),
        },
    )

    def get_s3_client(self) -> Any:
        return client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME'),
        )

    def get_bucket_name(self) -> str:
        return os.environ.get('AWS_STORAGE_BUCKET_NAME')

    def get_bucket_key(self, data_type: str, filename: str) -> str:
        return self.key_prefixes[data_type] + filename
