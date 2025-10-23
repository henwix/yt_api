from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class VideoNotFoundByKeyError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video not found by key'}

    key: str


@dataclass
class VideoNotFoundByUploadIdError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video not found by upload id'}

    upload_id: str


@dataclass
class VideoFilenameNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Video filename was not provided'}


@dataclass
class VideoFilenameNotSupportedFormatError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Unsupported video file format'}

    filename: str
