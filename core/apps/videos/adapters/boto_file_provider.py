from dataclasses import dataclass

from core.apps.videos.providers.videos import BaseBotoFileProvider


@dataclass
class BotoFileProvider(BaseBotoFileProvider):
    def _get_client_and_bucket(self) -> tuple:
        s3_client = self.boto_service.get_s3_client()
        bucket = self.boto_service.get_bucket_name()

        return s3_client, bucket

    def init_multipart_upload(self, filename: str, content_type: str = 'video/mp4') -> tuple:
        s3_client, bucket = self._get_client_and_bucket()

        response = s3_client.create_multipart_upload(
            Bucket=bucket,
            Key=self.boto_service.get_videos_bucket_key(filename=filename),
            ContentType=content_type,
        )

        return response

    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        s3_client, bucket = self._get_client_and_bucket()

        s3_client.abort_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
        )

    def generate_upload_part_url(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        expires_in: int = 120,
    ) -> str:
        s3_client, bucket = self._get_client_and_bucket()

        url = s3_client.generate_presigned_url(
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

    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        s3_client, bucket = self._get_client_and_bucket()

        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': key,
            },
            ExpiresIn=expires_in,
        )

        return url

    def complete_multipart_upload(self, key: str, upload_id: str, parts: list) -> dict:
        s3_client, bucket = self._get_client_and_bucket()

        response = s3_client.complete_multipart_upload(
            Bucket=bucket,
            Key=key,
            MultipartUpload={'Parts': parts},
            UploadId=upload_id,
        )

        return response

    def delete_object_by_key(self, key: str) -> None:
        s3_client, bucket = self._get_client_and_bucket()

        s3_client.delete_object(
            Bucket=bucket,
            Key=key,
        )
