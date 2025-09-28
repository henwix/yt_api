from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class UserNotFoundError(ServiceException):
    default_code = ErrorCodes.USER_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class UserWithThisDataAlreadyExistsError(ServiceException):
    default_code = ErrorCodes.USER_WITH_DATA_ALREADY_EXISTS
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class InvalidUIDValueError(ServiceException):
    default_code = ErrorCodes.IVALID_UID_VALUE
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    error_msg: str = ''


@dataclass
class UserAlreadyActivatedError(ServiceException):
    default_code = ErrorCodes.USER_ALREADY_ACTIVATED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    user_id: int


@dataclass
class UserActivationNotAllowedError(ServiceException):
    default_code = ErrorCodes.USER_ACTIVATION_NOT_ALLOWED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}
