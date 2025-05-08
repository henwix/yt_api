from dataclasses import dataclass

from core.apps.common.clients.boto_client import BotoClient
from core.apps.common.providers.files import BaseBotoFileProvider


@dataclass
class BotoFileProvider(BaseBotoFileProvider):
    boto_client: BotoClient

    def _get_client_and_bucket(self) -> tuple:
        client = self.boto_client.get_s3_client()
        bucket = self.boto_client.get_bucket_name()
        return client, bucket

    def create_multipart_upload(
        self,
        filename: str,
        data_type: str,
    ) -> tuple:
        client, bucket = self._get_client_and_bucket()
        key = self.boto_client.generate_unique_bucket_key(data_type=data_type, filename=filename)

        response = client.create_multipart_upload(
            Bucket=bucket,
            Key=key,
        )

        return response

    def abort_multipart_upload(
        self,
        key: str,
        upload_id: str,
    ) -> None:
        client, bucket = self._get_client_and_bucket()

        client.abort_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
        )

    def generate_upload_part_url(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        expires_in: int,
    ) -> str:
        client, bucket = self._get_client_and_bucket()

        url = client.generate_presigned_url(
            ClientMethod='upload_part',
            Params={
                'Bucket': bucket,
                'Key': key,
                'UploadId': upload_id,
                'PartNumber': part_number,
            },
            ExpiresIn=expires_in,
        )
        return url

    def generate_download_url(
        self,
        key: str,
        expires_in: int,
    ) -> str:
        client, bucket = self._get_client_and_bucket()

        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': key,
            },
            ExpiresIn=expires_in,
        )

        return url

    def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: list,
    ) -> dict:
        client, bucket = self._get_client_and_bucket()

        response = client.complete_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts},
        )

        return response

    def delete_object_by_key(
        self,
        key: str,
    ) -> None:
        client, bucket = self._get_client_and_bucket()

        client.delete_object(
            Bucket=bucket,
            Key=key,
        )

    def delete_objects(
        self,
        objects: list[dict],
    ) -> dict:
        client, bucket = self._get_client_and_bucket()

        response = client.delete_objects(
            Bucket=bucket,
            Delete={'Objects': objects},
        )

        return response

    def generate_upload_url(
        self,
        filename: str,
        expires_in: int,
        data_type: str,
    ) -> tuple:
        client, bucket = self._get_client_and_bucket()
        key = self.boto_client.generate_unique_bucket_key(data_type=data_type, filename=filename)

        url = client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket,
                'Key': key,
            },
            ExpiresIn=expires_in,
        )

        return url, key

    def head_object(self, key: str) -> None:
        """Check if object exists in S3 bucket.

        Args:
            key: The key of the object to check

        Raises:
            ClientError: If object does not exist or other S3 error occurs

        """
        client, bucket = self._get_client_and_bucket()

        client.head_object(Bucket=bucket, Key=key)
