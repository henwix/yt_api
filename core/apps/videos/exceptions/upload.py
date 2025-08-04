from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class VideoNotFoundByKeyError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video not found by key'}

    key: str

    @property
    def message(self):
        return 'Video not found by key'


@dataclass
class VideoNotFoundByUploadIdError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video not found by upload_id'}

    upload_id: str

    @property
    def message(self):
        return 'Video not found by upload_id'


@dataclass
class VideoFilenameNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Video filename not provided'}

    @property
    def message(self):
        return 'Video filename not provided'


@dataclass
class VideoFilenameFormatError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Unsupported video file format'}

    filename: str

    @property
    def message(self):
        return 'Unsupported video file format'
