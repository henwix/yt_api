from drf_spectacular.utils import OpenApiExample

from core.apps.common.errors import (
    ErrorCodes,
    ERRORS,
)


def detail_response_example(
    name: str,
    value: str,
    status_code: int,
    summary: str = '',
    description: str = '',
) -> OpenApiExample:
    """Return response example with custom 'detail' value."""

    return OpenApiExample(
        name=name,
        value={'detail': value},
        response_only=True,
        status_codes=[status_code],
        summary=summary,
        description=description,
    )


def error_response_example(error: dict, summary: str = '', description: str = '') -> OpenApiExample:
    """Create response example using name, error message and status code from
    provided Error dict."""

    return detail_response_example(
        name=error['message'] + ' error',
        value=error['message'],
        status_code=error['status_code'],
        summary=summary,
        description=description,
    )


def like_created_response_example() -> OpenApiExample:
    """Create response example for LikeCreation with 'Success' detail message
    and 'is_like' field."""

    return OpenApiExample(
        name='Created',
        value={'detail': 'Success', 'is_like': True},
        response_only=True,
        status_codes=[201],
    )


def jwt_response_example() -> OpenApiExample:
    """Create response example for JWT with 'access' and 'refresh' tokens."""

    return OpenApiExample(
        name='JWT',
        value={'access': 'string', 'refresh': 'string'},
        response_only=True,
        status_codes=[200],
    )


def captcha_validation_failed_response_example() -> OpenApiExample:
    return detail_response_example(
        name='Captcha validation failed',
        value=ERRORS[ErrorCodes.CAPTCHA_VALIDATION_FAILED]['message'],
        status_code=ERRORS[ErrorCodes.CAPTCHA_VALIDATION_FAILED]['status_code'],
    )


def captcha_token_not_provided_error_response_example() -> OpenApiExample:
    return detail_response_example(
        name='Captcha token not provided error',
        value=ERRORS[ErrorCodes.CAPTCHA_TOKEN_NOT_PROVIDED]['message'],
        status_code=ERRORS[ErrorCodes.CAPTCHA_TOKEN_NOT_PROVIDED]['status_code'],
    )


def created_response_example() -> OpenApiExample:
    """Create response example for Creation with 'Success' detail message."""
    return detail_response_example(name='Created', value='Success', status_code=201)


def deleted_response_example() -> OpenApiExample:
    """Create response example for Deletion with 'Success' detail message."""
    return detail_response_example(name='Deleted', value='Success', status_code=200)
