import uuid
from dataclasses import (
    dataclass,
    field,
)
from typing import Any

from django.conf import settings

from boto3 import client


@dataclass
class BotoClient:
    key_prefixes: dict = field(
        default_factory=lambda: {
            'video': settings.AWS_S3_VIDEO_BUCKET_PREFIX,
            'avatar': settings.AWS_S3_AVATAR_BUCKET_PREFIX,
        },
    )

    def get_s3_client(self) -> Any:
        return client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

    def get_bucket_name(self) -> str:
        return settings.AWS_STORAGE_BUCKET_NAME

    def generate_unique_bucket_key(self, data_type: str, filename: str) -> str:
        """Add 'data_type' bucket prefix and random uuid to 'filename'."""
        return self.key_prefixes[data_type] + uuid.uuid4().hex[:10] + '_' + filename
