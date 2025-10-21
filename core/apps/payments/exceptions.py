from dataclasses import dataclass
from typing import Any

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.payments.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class StripeInvalidSubTierError(ServiceException):
    default_code = ErrorCodes.STRIPE_INVALID_SUB_TIER_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    sub_tier: str


@dataclass
class StripeInvalidSubPriceError(ServiceException):
    default_code = ErrorCodes.STRIPE_INVALID_SUB_PRICE_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    sub_price: str


@dataclass
class StripeSubAlreadyExistsError(ServiceException):
    default_code = ErrorCodes.STRIPE_SUB_ALREADY_EXISTS_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    customer_id: str


@dataclass
class StripeSignatureVerificationError(ServiceException):
    default_code = ErrorCodes.STRIPE_SIGNATURE_VERIFICATION_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    error_msg: str


@dataclass
class StripeCustomerIdIsNotStringError(ServiceException):
    default_code = ErrorCodes.STRIPE_CUSTOMER_ID_IS_NOT_STRING_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    customer_id: Any
    customer_id_type: type


@dataclass
class StripeNotAllowedEventTypeError(ServiceException):
    default_code = ErrorCodes.STRIPE_NOT_ALLOWED_EVENT_TYPE_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    event_type: str
