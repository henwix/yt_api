from rest_framework import serializers
from rest_framework.response import Serializer

from drf_spectacular.utils import (
    inline_serializer,
    OpenApiExample,
    OpenApiResponse,
)

from core.apps.common.errors import (
    ErrorCodes,
    ERRORS,
)
from core.apps.common.exceptions.exceptions import ServiceException


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


def build_example_response_from_error(
    error: ServiceException,
    summary: str = '',
    description: str = '',
) -> OpenApiExample:
    return OpenApiExample(
        name=error.default_detail['detail'] + ' error',
        value=error.default_detail,
        response_only=True,
        status_codes=[error.status_code],
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


def jwt_response_example(description: str = '') -> OpenApiExample:
    """Create response example for JWT with 'access' and 'refresh' tokens."""

    return OpenApiExample(
        name='JWT',
        value={'access': 'string', 'refresh': 'string'},
        response_only=True,
        status_codes=[200],
        description=description,
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


def confirmation_email_sent_response_example() -> OpenApiExample:
    return detail_response_example(
        name='Confirmation email has been sent',
        value='Confirmation email successfully sent',
        status_code=200,
    )


def build_paginated_response_based_on_serializer(
    serializer: Serializer,
    pagination_type: str = 'cursor',
    description: str = '',
) -> OpenApiResponse:
    """
    params:
        - serializer: Serializer - serializer that will be used to build the response
        - pagination_type: str - 'cursor' or 'page'
        - description: str - description for response

    Build paginated response based on the provided serializer and pagination type.

    Usually used in "@action" endpoints, where drf_spectacular doesn't add pagination fields.
    """

    if pagination_type == 'cursor':
        pagination_fields = {
            'next': serializers.URLField(
                allow_null=True,
                default='http://api.example.org/accounts/?c=cD00ODY%253D%22',
            ),
            'previous': serializers.URLField(
                allow_null=True,
                default='http://api.example.org/accounts/?c=cj0xJnA9NDg3',
            ),
        }
    else:
        pagination_fields = {
            'count': serializers.IntegerField(default=123),
            'next': serializers.URLField(allow_null=True, default='http://api.example.org/accounts/?page=4'),
            'previous': serializers.URLField(allow_null=True, default='http://api.example.org/accounts/?page=2'),
        }
    pagination_fields.update({'results': serializer(many=True)})

    return OpenApiResponse(
        response=inline_serializer(
            name=f'Paginated{serializer.__name__}',
            fields=pagination_fields,
        ),
        description=description,
    )
