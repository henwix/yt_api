from drf_spectacular.utils import OpenApiExample

from core.api.v1.schema.response_examples.common import detail_response_example


def oauth2_connected_providers_response_example() -> OpenApiExample:
    return OpenApiExample(
        name='Connected',
        value={'connected': {'github': True, 'google': False, 'x': True}},
        response_only=True,
        status_codes=[200],
    )


def social_auth_error_response_example() -> OpenApiExample:
    return detail_response_example(
        name='OAuth2 Error',
        value='string',
        status_code=400,
        description='Returns this response if something went wrong with the OAuth2 flow',
    )
