from dataclasses import dataclass

from core.apps.common.providers.captcha import BaseCaptchaProvider


@dataclass
class DummyCaptchaProvider(BaseCaptchaProvider):
    response: dict

    def validate_token(self, token: str, remoteip: str = None) -> dict:
        return self.response
