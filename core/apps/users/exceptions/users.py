from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class UserNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'User not found'}


@dataclass
class UserWithThisDataAlreadyExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'User with this data already exists'}


@dataclass
class InvalidUIDValueError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Invalid uid value'}

    error_msg: str = ''


@dataclass
class UserAlreadyActivatedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'User already activated'}

    user_id: int


@dataclass
class UserActivationNotAllowedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'User activation not allowed'}
