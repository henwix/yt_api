from dataclasses import dataclass

from rest_framework import status

from social_core.exceptions import AuthException

from core.apps.common.exceptions.exceptions import ServiceException


class CustomAuthStateMissing(AuthException):
    """Custom exception raised when the 'state' parameter is invalid.

    The __str__ message has been customized to exclude any mention of
    sessions, as sessions are not used in this implementation.

    """
    def __str__(self):
        return "Storage value state missing."


@dataclass
class OAuth2NotImplementedProvider(ServiceException):
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'This provider is not implemented for OAuth2 authorization'}

    provider: str

    @property
    def message(self):
        return 'OAuth2 invalid provider'
