from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.videos.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class VideoNotFoundByKeyError(ServiceException):
    default_code = ErrorCodes.VIDEO_NOT_FOUND_BY_KEY
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    key: str


@dataclass
class VideoNotFoundByUploadIdError(ServiceException):
    default_code = ErrorCodes.VIDEO_NOT_FOUND_BY_UPLOAD_ID
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    upload_id: str


@dataclass
class VideoFilenameNotProvidedError(ServiceException):
    default_code = ErrorCodes.VIDEO_FILENAME_NOT_PROVIDED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class VideoFilenameFormatError(ServiceException):
    default_code = ErrorCodes.VIDEO_FILENAME_FORMAT_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    filename: str
