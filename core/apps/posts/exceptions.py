from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.posts.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class PostAuthorSlugNotProvidedError(ServiceException):
    default_code = ErrorCodes.POST_AUTHOR_SLUG_NOT_PROVIDED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class PostNotFoundError(ServiceException):
    default_code = ErrorCodes.POST_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    post_id: str | None = None


@dataclass
class PostLikeNotFoundError(ServiceException):
    default_code = ErrorCodes.POST_LIKE_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    channel_slug: str | None = None
    post_id: str | None = None
