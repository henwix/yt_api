from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from django.conf import settings

import requests


@dataclass
class BaseCaptchaProvider(ABC):
    @abstractmethod
    def validate_token(self, token: str, remoteip: str | None = None) -> dict:
        ...


class GoogleCaptchaProvider(BaseCaptchaProvider):
    CAPTCHA_PRIVATE_KEY = settings.V3_GOOGLE_RECAPTCHA_PRIVATE_KEY
    CAPTCHA_DEFAULT_URL = settings.GOOGLE_RECAPTCHA_DEFAULT_URL

    def validate_token(self, token: str, remoteip: str | None = None) -> dict:
        response = requests.post(
            self.CAPTCHA_DEFAULT_URL, data={
                'secret': self.CAPTCHA_PRIVATE_KEY,
                'response': token,
                'remoteip': remoteip,
            },
        ).json()

        return response
