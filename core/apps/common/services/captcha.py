from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from logging import Logger

from django.conf import settings

from core.apps.common.exceptions.captcha import (
    CaptchaTokenNotProvidedError,
    CaptchaValidationFailed,
)
from core.apps.common.providers.captcha import BaseCaptchaProvider


@dataclass
class BaseCaptchaService(ABC):
    captcha_provider: BaseCaptchaProvider
    logger: Logger

    @abstractmethod
    def validate(self, token: str | None, captcha_required: bool, remoteip: str | None = None) -> bool:
        ...


class GoogleV3CaptchaService(BaseCaptchaService):
    def validate(self, token: str | None, captcha_required: bool, remoteip: str | None = None) -> bool:
        if token is None:
            if captcha_required:
                raise CaptchaTokenNotProvidedError()
            return True

        result = self.captcha_provider.validate(token=token, remoteip=remoteip)

        if result['success']:
            if result['score'] > settings.V3_MIN_GOOGLE_RECAPTCHA_SCORE:
                return True
            raise CaptchaValidationFailed(score=result['score'])
        else:
            raise CaptchaValidationFailed(error_code=result['error-codes'][0])
