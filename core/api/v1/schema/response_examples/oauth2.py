from drf_spectacular.utils import OpenApiExample


def oauth2_connected_providers_response_example() -> OpenApiExample:
    return OpenApiExample(
        name='Connected',
        value={'connected': {'github': True, 'google': False, 'x': True}},
        response_only=True,
        status_codes=[200],
    )
