from dataclasses import dataclass

from rest_framework import status

from social_core.exceptions import AuthException

from core.apps.common.exceptions.exceptions import ServiceException


class CustomAuthStateMissing(AuthException):
    """State parameter is incorrect."""

    def __str__(self):
        return "Storage value state missing."


@dataclass
class OAuth2NotImplementedProvider(ServiceException):
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'This provider is not implemented for OAuth2 authorization'}

    provider: str

    @property
    def message(self):
        return 'OAuth2 invalid provider'
