from drf_spectacular.utils import OpenApiExample


def multipart_upload_created_response_example() -> OpenApiExample:
    return OpenApiExample(
        name='Created',
        value={'upload_id': 'test_upload_id', 'key': 'videos/test_key.mp4'},
        response_only=True,
        status_codes=[201],
    )


def multipart_upload_part_url_response_example() -> OpenApiExample:
    return OpenApiExample(
        name='Created',
        value={'upload_url': 'test_upload_url'},
        response_only=True,
        status_codes=[201],
    )
