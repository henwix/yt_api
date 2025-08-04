from drf_spectacular.utils import OpenApiExample


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


def like_created_response_example() -> OpenApiExample:
    return OpenApiExample(
        name='Created',
        value={'detail': 'Success', 'is_like': True},
        response_only=True,
        status_codes=[201],
    )


def jwt_response_example() -> OpenApiExample:
    return OpenApiExample(
        name='JWT',
        value={'access': 'string', 'refresh': 'string'},
        response_only=True,
        status_codes=[200],
    )


def url_response_example() -> OpenApiExample:
    return OpenApiExample(
        name='URL',
        value={'access': 'string', 'refresh': 'string'},
        response_only=True,
        status_codes=[200],
    )
