from social_core.exceptions import AuthException


class CustomAuthStateMissing(AuthException):
    """State parameter is incorrect."""

    def __str__(self):
        return "Storage value state missing."
