from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class OtpCodeNotProvidedOrNotFoundException(ServiceException):
    default_code = ErrorCodes.OTP_CODE_NOT_PROVIDED_OR_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    email: str


@dataclass
class OtpCodeNotEqualException(ServiceException):
    default_code = ErrorCodes.CODE_NOT_EQUAL
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    cached_code: str
    user_code: str


@dataclass
class SetEmailCodeNotProvidedOrNotFoundException(ServiceException):
    default_code = ErrorCodes.SET_EMAIL_CODE_NOT_PROVIDED_OR_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    user_code: str


@dataclass
class SetEmailUserNotEqualException(ServiceException):
    default_code = ErrorCodes.SET_EMAIL_USER_NOT_EQUAL
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    cached_user_id: int


@dataclass
class ResetPasswordCodeNotProvidedOrNotFoundException(ServiceException):
    default_code = ErrorCodes.RESET_PASSWORD_CODE_NOT_NOT_PROVIDED_OR_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    code: str


@dataclass
class ResetPasswordCodeNotEqualException(ServiceException):
    default_code = ErrorCodes.RESET_PASSWORD_CODE_NOT_EQUAL
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    code: str


@dataclass
class ResetUsernameCodeNotProvidedOrNotFoundException(ServiceException):
    default_code = ErrorCodes.RESET_USERNAME_CODE_NOT_NOT_PROVIDED_OR_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    code: str


@dataclass
class ResetUsernameCodeNotEqualException(ServiceException):
    default_code = ErrorCodes.RESET_USERNAME_CODE_NOT_EQUAL
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int
    code: str
