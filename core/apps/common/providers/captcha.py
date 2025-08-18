from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

import requests


@dataclass
class BaseCaptchaProvider(ABC):
    @abstractmethod
    def validate_token(
        self,
        secret: str,
        token: str,
        remoteip: str | None = None,
    ) -> dict:
        ...


class GoogleCaptchaProvider(BaseCaptchaProvider):
    def validate_token(
        self,
        secret: str,
        token: str,
        remoteip: str | None = None,
    ) -> dict:
        response = requests.post(
            url='https://www.google.com/recaptcha/api/siteverify', data={
                'secret': secret,
                'response': token,
                'remoteip': remoteip,
            },
        ).json()

        return response
