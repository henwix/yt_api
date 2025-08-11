from drf_spectacular.utils import OpenApiExample

from core.api.v1.schema.response_examples.common import detail_response_example


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


def s3_error_response_example() -> OpenApiExample:
    return detail_response_example(name='S3 error', value='string', status_code=500)


def multipart_upload_complete_request_example() -> OpenApiExample:
    return OpenApiExample(
        name='Request',
        value={
            'key': 'string',
            'upload_id': 'string',
            'parts': [
                {
                    'ETag': 'string',
                    'PartNumber': 1,
                },
                {
                    'ETag': 'string',
                    'PartNumber': 2,
                },
                {
                    'ETag': 'string',
                    'PartNumber': 3,
                },
            ],
        },
        request_only=True,
    )
