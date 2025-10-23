from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class AvatarFilenameNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Avatar filename not provided'}


@dataclass
class AvatarFilenameNotSupportedFormatError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Unsupported avatar file format'}

    filename: str
