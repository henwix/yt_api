from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


@dataclass
class AvatarFilenameNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Avatar filename not provided'}

    @property
    def message(self):
        return 'Avatar filename not provided'


@dataclass
class AvatarFilenameFormatError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Unsupported avatar file format'}

    filename: str

    @property
    def message(self):
        return 'Unsupported avatar file format'
