from dataclasses import dataclass

from core.apps.channels.errors import (
    ErrorCodes,
    ERRORS,
)
from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class AvatarFilenameNotProvidedError(ServiceException):
    default_code = ErrorCodes.AVATAR_FILENAME_NOT_PROVIDED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class AvatarFilenameFormatError(ServiceException):
    default_code = ErrorCodes.AVATAR_FILENAME_FORMAT_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    filename: str
