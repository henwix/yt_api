from dataclasses import dataclass

from core.apps.channels.errors import (
    ErrorCodes,
    ERRORS,
)
from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class ChannelNotFoundError(ServiceException):
    default_code = ErrorCodes.CHANNEL_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int | str


@dataclass
class SlugChannelNotFoundError(ServiceException):
    default_code = ErrorCodes.SLUG_CHANNEL_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    channel_slug: str


@dataclass
class AvatarDoesNotExistsError(ServiceException):
    default_code = ErrorCodes.AVATAR_DOES_NOT_EXIST
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    channel_slug: str
