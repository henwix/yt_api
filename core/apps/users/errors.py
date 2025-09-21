from rest_framework import status


class ErrorCodes:
    # users/exceptions/codes.py
    CODE_NOT_PROVIDED = "code_not_provided"
    CODE_NOT_EQUAL = "code_not_equal"

    # users/exceptions/oauth2.py
    OAUTH2_PROVIDER_NOT_SUPPORTED = "oauth2_provider_not_supported"

    # users/exceptions/users.py
    USER_NOT_FOUND = "user_not_found"
    USER_WITH_DATA_ALREADY_EXISTS = "user_with_data_already_exists"


ERRORS = {
    # users/exceptions/codes.py
    ErrorCodes.CODE_NOT_PROVIDED: {
        'message': 'Code not provided',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.CODE_NOT_EQUAL: {
        'message': 'Code not equal',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },

    # users/exceptions/oauth2.py
    ErrorCodes.OAUTH2_PROVIDER_NOT_SUPPORTED: {
        'message': 'This provider is not implemented for OAuth2 authorization',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },

    # users/exceptions/users.py
    ErrorCodes.USER_NOT_FOUND: {
        'message': 'User not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.USER_WITH_DATA_ALREADY_EXISTS: {
        'message': 'User with this data already exists',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
}
