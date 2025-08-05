from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class CodeNotProvidedException(ServiceException):
    default_code = ErrorCodes.CODE_NOT_PROVIDED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    email: str


@dataclass
class CodeNotEqualException(ServiceException):
    default_code = ErrorCodes.CODE_NOT_EQUAL
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    cached_code: str
    user_code: str
