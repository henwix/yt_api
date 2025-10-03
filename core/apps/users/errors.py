from rest_framework import status


class ErrorCodes:
    # users/exceptions/codes.py
    OTP_CODE_NOT_PROVIDED_OR_NOT_FOUND = 'otp_code_not_provided'
    CODE_NOT_EQUAL = 'otp_code_not_equal'
    SET_EMAIL_CODE_NOT_PROVIDED_OR_NOT_FOUND = 'set_email_code_not_provided'
    SET_EMAIL_USER_NOT_EQUAL = 'set_email_user_not_equal'
    USER_EMAIL_CODE_NOT_FOUND = 'user_email_code_not_found'
    RESET_CODE_NOT_EQUAL = 'user_email_code_not_equal'

    # users/exceptions/oauth2.py
    OAUTH2_PROVIDER_NOT_SUPPORTED = 'oauth2_provider_not_supported'

    # users/exceptions/users.py
    USER_NOT_FOUND = 'user_not_found'
    USER_WITH_DATA_ALREADY_EXISTS = 'user_with_data_already_exists'
    IVALID_UID_VALUE = 'invalid_uid_value'
    USER_ALREADY_ACTIVATED = 'user_already_activated'
    USER_ACTIVATION_NOT_ALLOWED = 'user_activation_not_allowed'


ERRORS = {
    # users/exceptions/codes.py
    ErrorCodes.OTP_CODE_NOT_PROVIDED_OR_NOT_FOUND: {
        'message': 'Otp code not provided or not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.CODE_NOT_EQUAL: {
        'message': 'Otp code not equal',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.SET_EMAIL_CODE_NOT_PROVIDED_OR_NOT_FOUND: {
        'message': 'Set email code not provided or not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.SET_EMAIL_USER_NOT_EQUAL: {
        'message': 'Set email user not equal',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.USER_EMAIL_CODE_NOT_FOUND: {
        'message': 'Reset code not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.RESET_CODE_NOT_EQUAL: {
        'message': 'Reset code not equal',
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
    ErrorCodes.IVALID_UID_VALUE: {
        'message': 'Invalid uid value',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.USER_ALREADY_ACTIVATED: {
        'message': 'User already activated',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.USER_ACTIVATION_NOT_ALLOWED: {
        'message': 'User activation not allowed',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
}
