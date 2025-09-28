from dataclasses import dataclass

from social_core.exceptions import AuthException

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.errors import (
    ErrorCodes,
    ERRORS,
)


class CustomAuthStateMissing(AuthException):
    """Custom exception raised when the 'state' parameter is invalid.

    The __str__ message has been customized to exclude any mention of
    sessions, as sessions are not used in this implementation.

    """
    def __str__(self):
        return "Storage value state missing."


@dataclass
class OAuth2NotImplementedProviderError(ServiceException):
    default_code = ErrorCodes.OAUTH2_PROVIDER_NOT_SUPPORTED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    provider: str
