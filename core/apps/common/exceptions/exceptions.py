from dataclasses import dataclass

from rest_framework import status
from rest_framework.exceptions import APIException


@dataclass
class ServiceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Application exception occurred'}

    def __post_init__(self):
        super().__init__()

    @property
    def message(self):
        return self.default_detail['detail']


@dataclass
class S3FileWithKeyNotExistError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'File with this key does not exist in S3'}

    key: str


@dataclass
class MultipartUploadDoesNotExistError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Multipart upload with this key and upload_id does not exist in S3'}

    key: str
    upload_id: str
