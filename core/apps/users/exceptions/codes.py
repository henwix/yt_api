from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class OtpCodeNotFoundError(ServiceException):
    default_code = ErrorCodes.OTP_CODE_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    email: str


@dataclass
class OtpCodeNotEqualError(ServiceException):
    default_code = ErrorCodes.CODE_NOT_EQUAL
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    cached_code: str
    user_code: str


@dataclass
class SetEmailCodeNotProvidedOrNotFoundError(ServiceException):
    default_code = ErrorCodes.SET_EMAIL_CODE_NOT_PROVIDED_OR_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    user_code: str


@dataclass
class SetEmailUserNotEqualError(ServiceException):
    default_code = ErrorCodes.SET_EMAIL_USER_NOT_EQUAL
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    cached_user_id: int


@dataclass
class UserEmailCodeNotFoundError(ServiceException):
    default_code = ErrorCodes.USER_EMAIL_CODE_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    code: str


@dataclass
class UserEmailCodeNotEqualError(ServiceException):
    default_code = ErrorCodes.USER_EMAIL_CODE_NOT_EQUAL
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    code: str
