from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from logging import Logger

from core.apps.common.constants import V3_MIN_GOOGLE_RECAPTCHA_SCORE
from core.apps.common.exceptions.captcha import (
    CaptchaTokenNotProvidedError,
    CaptchaValidationFailedError,
)
from core.apps.common.providers.captcha import BaseCaptchaProvider


@dataclass
class BaseCaptchaService(ABC):
    captcha_provider: BaseCaptchaProvider
    logger: Logger

    @abstractmethod
    def validate_token(
        self,
        version: str,
        token: str | None,
        remoteip: str | None = None,
    ) -> bool: ...


class GoogleV3CaptchaService(BaseCaptchaService):
    def validate_token(
        self,
        version: str,
        token: str | None,
        remoteip: str | None = None,
    ) -> bool:
        """Validate token from Google reCAPTCHA v3."""

        if token is None:
            raise CaptchaTokenNotProvidedError()

        result = self.captcha_provider.validate_token(
            version=version,
            token=token,
            remoteip=remoteip,
        )

        if result.get('success', False):  # check if the 'success' is in the result and not equal to False
            if result.get('score', 0) > V3_MIN_GOOGLE_RECAPTCHA_SCORE:  # check 'score' from the result
                return True
            raise CaptchaValidationFailedError(score=result.get('score'))

        # raise an error if the 'success' from the result equals to False
        raise CaptchaValidationFailedError(error_code=result.get('error-codes', ['unknown-error'])[0])


class GoogleV2CaptchaService(BaseCaptchaService):
    def validate_token(
        self,
        version: str,
        token: str | None,
        remoteip: str | None = None,
    ) -> bool:
        """Validate token from Google reCAPTCHA v2."""

        if token is None:
            raise CaptchaTokenNotProvidedError()

        result = self.captcha_provider.validate_token(
            version=version,
            token=token,
            remoteip=remoteip,
        )

        if result.get('success', False):  # check if the 'success' is in the result and not equal to False
            return True

        # raise an error if the 'success' from the result equals to False
        raise CaptchaValidationFailedError(error_code=result.get('error-codes', ['unknown-error'])[0])
