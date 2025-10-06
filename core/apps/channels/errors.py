from rest_framework import status


class ErrorCodes:
    # channels/exceptions/channels.py
    CHANNEL_NOT_FOUND = "channel_not_found"
    SLUG_CHANNEL_NOT_FOUND = "slug_channel_not_found"
    AVATAR_DOES_NOT_EXIST = "avatar_does_not_exist"
    CHANNEL_SLUG_INVALID_VALUE = 'channel_slug_invalid_value'

    # channels/exceptions/subscriptions.py
    SELF_SUBSCRIPTION = "self_subscription"
    SUBSCRIPTION_EXISTS = "subscription_exists"
    SUBSCRIPTION_DOES_NOT_EXIST = "subscription_does_not_exist"

    # channels/exceptions/upload.py
    AVATAR_FILENAME_NOT_PROVIDED = "avatar_filename_not_provided"
    AVATAR_FILENAME_FORMAT_ERROR = "avatar_filename_format_error"


ERRORS = {
    # channels/exceptions/channels.py
    ErrorCodes.CHANNEL_NOT_FOUND: {
        'message': 'Channel not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.SLUG_CHANNEL_NOT_FOUND: {
        'message': 'Channel with this slug is not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.AVATAR_DOES_NOT_EXIST: {
        'message': 'Avatar does not exist',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.CHANNEL_SLUG_INVALID_VALUE: {
        'message': 'Channel slug invalid value',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },

    # channels/exceptions/subscriptions.py
    ErrorCodes.SELF_SUBSCRIPTION: {
        'message': "You can't subscribe/unsubscribe to/from yourself",
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.SUBSCRIPTION_EXISTS: {
        'message': 'Subscription already exists',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.SUBSCRIPTION_DOES_NOT_EXIST: {
        'message': 'Subscription does not exist',
        'status_code': status.HTTP_404_NOT_FOUND,
    },

    # channels/exceptions/upload.py
    ErrorCodes.AVATAR_FILENAME_NOT_PROVIDED: {
        'message': 'Avatar filename not provided',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.AVATAR_FILENAME_FORMAT_ERROR: {
        'message': 'Unsupported avatar file format',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
}
