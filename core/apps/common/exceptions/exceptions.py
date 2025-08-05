from dataclasses import dataclass

from rest_framework.exceptions import APIException

from core.apps.common.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class ServiceException(APIException):
    default_code = ErrorCodes.SERVICE_EXCEPTION
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    def __post_init__(self):
        super().__init__()

    # def __str__(self):  # add this if you need to remove 'details' field from logs
    #     return str({k:v for k, v in self.__dict__.items() if k != 'details'})

    @property
    def message(self):
        return self.default_detail['detail']


@dataclass
class S3FileWithKeyNotExistsError(ServiceException):
    default_code = ErrorCodes.S3_FILE_WITH_KEY_NOT_EXISTS
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    key: str


@dataclass
class MultipartUploadExistsError(ServiceException):
    default_code = ErrorCodes.MULTIPART_UPLOAD_EXISTS_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    key: str
    upload_id: str
