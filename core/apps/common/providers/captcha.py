from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

import requests

from core.apps.common.constants import CAPTCHA_SECRET_KEYS
from core.apps.common.exceptions.captcha import CaptchaTokenVerifyRequestError


@dataclass
class BaseCaptchaProvider(ABC):
    @abstractmethod
    def validate_token(
        self,
        version: str,
        token: str,
        remoteip: str | None = None,
    ) -> dict: ...


class GoogleCaptchaProvider(BaseCaptchaProvider):
    def validate_token(
        self,
        version: str,
        token: str,
        remoteip: str | None = None,
    ) -> dict:
        try:
            response = requests.post(
                url='https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': CAPTCHA_SECRET_KEYS.get(version),
                    'response': token,
                    'remoteip': remoteip,
                },
            ).json()
        except requests.exceptions.RequestException as error:
            raise CaptchaTokenVerifyRequestError(version=version, error=str(error))

        return response
