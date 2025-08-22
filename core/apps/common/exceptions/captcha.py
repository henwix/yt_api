from dataclasses import dataclass

from core.apps.common.errors import (
    ErrorCodes,
    ERRORS,
)
from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class CaptchaTokenNotProvidedError(ServiceException):
    default_code = ErrorCodes.CAPTCHA_TOKEN_NOT_PROVIDED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class CaptchaValidationFailed(ServiceException):
    default_code = ErrorCodes.CAPTCHA_VALIDATION_FAILED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    error_code: str | None = None
    score: float | None = None


@dataclass
class CaptchaVersionNotSupported(ServiceException):
    default_code = ErrorCodes.CAPTCHA_VERSION_NOT_SUPPORTED_OR_NOT_PROVIDED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    version: str


@dataclass
class CaptchaVerifyRequestError(ServiceException):
    default_code = ErrorCodes.CAPTCHA_VERIFY_REQUEST_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    version: str
    error: str
