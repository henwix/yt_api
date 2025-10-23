from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class CaptchaTokenNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Captcha token not provided'}


@dataclass
class CaptchaValidationFailedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Captcha validation failed'}

    error_code: str | None = None
    score: float | None = None


@dataclass
class CaptchaVersionNotSupportedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Captcha version not supported or not provided'}

    version: str


@dataclass
class CaptchaTokenVerifyRequestError(ServiceException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = {'detail': 'Captcha token verify request error'}

    version: str
    error: str
