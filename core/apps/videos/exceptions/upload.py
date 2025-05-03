from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


@dataclass
class VideoNotFoundByUploadIdError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Video not found by upload_id'}

    upload_id: str = None

    @property
    def message(self):
        return 'Video not found by upload_id'


@dataclass
class VideoNotFoundByKeyError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Video not found by key'}

    key: str

    @property
    def message(self):
        return 'Video not found by key'


@dataclass
class FilenameNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Filename not provided'}

    @property
    def message(self):
        return 'Filename not provided'


@dataclass
class UnsupportedFileFormatError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Unsupported file format'}

    filename: str

    @property
    def message(self):
        return 'Unsupported file format'
