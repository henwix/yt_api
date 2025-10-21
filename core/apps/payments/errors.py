from rest_framework import status


class ErrorCodes:
    STRIPE_INVALID_SUB_TIER_ERROR = 'stripe_wrong_sub_tier_error'
    STRIPE_INVALID_SUB_PRICE_ERROR = 'stripe_wrong_sub_price_error'
    STRIPE_SUB_ALREADY_EXISTS_ERROR = 'stripe_sub_already_exists_error'
    STRIPE_SIGNATURE_VERIFICATION_ERROR = 'stripe_signature_verification_error'
    STRIPE_CUSTOMER_ID_IS_NOT_STRING_ERROR = 'stripe_customer_id_not_string_error'
    STRIPE_NOT_ALLOWED_EVENT_TYPE_ERROR = 'stripe_not_allowed_event_type_error'


ERRORS = {
    ErrorCodes.STRIPE_INVALID_SUB_TIER_ERROR: {
        'message': 'Stripe invalid sub tier',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.STRIPE_INVALID_SUB_PRICE_ERROR: {
        'message': 'Stripe invalid sub price',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.STRIPE_SUB_ALREADY_EXISTS_ERROR: {
        'message': 'Stripe sub already exists',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.STRIPE_SIGNATURE_VERIFICATION_ERROR: {
        'message': 'Stripe signature verification error',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.STRIPE_CUSTOMER_ID_IS_NOT_STRING_ERROR: {
        'message': 'Stripe customer ID is not string',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.STRIPE_NOT_ALLOWED_EVENT_TYPE_ERROR: {
        'message': 'Stripe not allowed event type',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
}
