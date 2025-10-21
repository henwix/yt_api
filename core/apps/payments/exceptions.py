from dataclasses import dataclass
from typing import Any

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class StripeInvalidSubTierError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Stripe invalid sub tier'}

    sub_tier: str


@dataclass
class StripeInvalidSubPriceError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Stripe invalid sub price'}

    sub_price: str


@dataclass
class StripeSubAlreadyExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Stripe sub already exists'}

    customer_id: str


@dataclass
class StripeSignatureVerificationError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Stripe signature verification error'}

    error_msg: str


@dataclass
class StripeCustomerIdIsNotStringError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Stripe customer ID is not string'}

    customer_id: Any
    customer_id_type: type


@dataclass
class StripeNotAllowedEventTypeError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Stripe not allowed event type'}

    event_type: str
