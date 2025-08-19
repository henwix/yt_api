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
    def validate_token(
        self,
        version: str,
        token: str,
        remoteip: str | None = None,
    ) -> dict:
        ...


class GoogleCaptchaProvider(BaseCaptchaProvider):
    def validate_token(
        self,
        version: str,
        token: str,
        remoteip: str | None = None,
    ) -> dict:
        response = requests.post(
            url='https://www.google.com/recaptcha/api/siteverify', data={
                'secret': settings.CAPTCHA_SECRET_KEYS.get(version),
                'response': token,
                'remoteip': remoteip,
            },
        ).json()

        return response
