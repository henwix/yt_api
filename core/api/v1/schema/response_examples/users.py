from drf_spectacular.utils import OpenApiExample

from core.api.v1.schema.response_examples.common import detail_response_example


def user_email_updated_response_example() -> OpenApiExample:
    return OpenApiExample(
        name='Email has been updated',
        value={'detail': 'Success', 'new_email': 'user@example.com'},
        response_only=True,
        status_codes=[200],
    )


def user_activation_email_sent_response_example(status_code: int) -> OpenApiExample:
    return detail_response_example(
        name='Activation email sent',
        value='Activation email successfully sent',
        status_code=status_code,
        description="Returns this response if email activation is enabled and the user's account is \
        not yet activated",
    )


def user_created_response_example() -> OpenApiExample:
    value = {
        'id': 123,
        'email': 'user@example.com',
        'username': 'string',
        'otp_enabled': False,
        'channel': {
            'name': 'string',
            'slug': 'string',
            'description': 'string',
            'country': 'string',
            'avatar_s3_key': None,
        },
    }
    return OpenApiExample(
        name='User created',
        value=value,
        response_only=True,
        status_codes=[201],
        description="Returns this response if email activation is not enabled and the user's account is \
                already activated",
    )
