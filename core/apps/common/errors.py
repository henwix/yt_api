from rest_framework import status


class ErrorCodes:
    # common/exceptions/captcha.py
    CAPTCHA_TOKEN_NOT_PROVIDED = "captcha_token_not_provided"
    CAPTCHA_VALIDATION_FAILED = "captcha_validation_failed"

    # common/exceptions/comments.py
    COMMENT_NOT_FOUND = "comment_not_found"
    COMMENT_LIKE_NOT_FOUND = "comment_like_not_found"

    # common/exceptions/exceptions.py
    SERVICE_EXCEPTION = "service_exception"
    S3_FILE_WITH_KEY_NOT_EXISTS = "s3_file_with_key_not_exists"
    MULTIPART_UPLOAD_EXISTS_ERROR = "multipart_upload_exists"


ERRORS = {
    # common/exceptions/captcha.py
    ErrorCodes.CAPTCHA_TOKEN_NOT_PROVIDED: {
        'message': 'Captcha token not provided',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.CAPTCHA_VALIDATION_FAILED: {
        'message': 'Captcha validation failed',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },

    # common/exceptions/comments.py
    ErrorCodes.COMMENT_NOT_FOUND: {
        'message': 'Comment not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.COMMENT_LIKE_NOT_FOUND: {
        'message': 'Comment like or dislike not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },

    # common/exceptions/exceptions.py
    ErrorCodes.SERVICE_EXCEPTION: {
        'message': 'Application exception occurred',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.S3_FILE_WITH_KEY_NOT_EXISTS: {
        'message': 'File with this key does not exist in S3',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.MULTIPART_UPLOAD_EXISTS_ERROR: {
        'message': 'Multipart upload with this key and upload_id does not exist in S3',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
}
