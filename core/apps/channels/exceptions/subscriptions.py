from dataclasses import dataclass

from core.apps.channels.errors import (
    ErrorCodes,
    ERRORS,
)
from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class SelfSubscriptionError(ServiceException):
    default_code = ErrorCodes.SELF_SUBSCRIPTION
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    channel_slug: str


@dataclass
class SubscriptionExistsError(ServiceException):
    default_code = ErrorCodes.SUBSCRIPTION_EXISTS
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    sub_slug: str
    sub_to_slug: str


@dataclass
class SubscriptionDoesNotExistsError(ServiceException):
    default_code = ErrorCodes.SUBSCRIPTION_DOES_NOT_EXIST
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    sub_slug: str
    sub_to_slug: str
