from dataclasses import dataclass

from rest_framework import status
from rest_framework.exceptions import APIException


@dataclass
class ServiceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Application exception occurred'}

    def __post_init__(self):
        super().__init__()

    # def __str__(self):  # add this if you need to remove 'details' field from logs
    #     return str({k:v for k, v in self.__dict__.items() if k != 'details'})

    @property
    def message(self):
        return 'Application exception occurred'


@dataclass
class S3FileWithKeyNotExistsError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'File with this key does not exist in S3'}

    key: str

    @property
    def message(self):
        return 'File with this key does not exist in S3'
