from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class OtpCodeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Otp code not found'}

    email: str


@dataclass
class OtpCodeNotEqualError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Otp code not equal'}

    cached_code: str
    user_code: str


@dataclass
class SetEmailCodeNotProvidedOrNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Set email code not provided or not found'}

    user_id: int
    user_code: str


@dataclass
class SetEmailUserNotEqualError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Set email user not equal'}

    user_id: int
    cached_user_id: int


@dataclass
class UserEmailCodeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Email code not found'}

    user_id: int
    code: str


@dataclass
class UserEmailCodeNotEqualError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Email code not equal'}

    user_id: int
    code: str
