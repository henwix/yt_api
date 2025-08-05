from dataclasses import dataclass

from core.apps.common.errors import (
    ErrorCodes,
    ERRORS,
)
from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class CommentNotFoundError(ServiceException):
    default_code = ErrorCodes.COMMENT_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class CommentLikeNotFoundError(ServiceException):
    default_code = ErrorCodes.COMMENT_LIKE_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    channel_slug: str
    comment_id: int
