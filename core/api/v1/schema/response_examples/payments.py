from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from core.api.v1.schema.response_examples.common import detail_response_example


def retrieve_subscription_state_response_example() -> OpenApiResponse:
    value = {
        'sub_state': {
            'subscription_id': 'string',
            'customer_id': 'string',
            'status': 'active',
            'price_id': 'string',
            'tier': 'pro',
            'current_period_start': 1762374438,
            'current_period_end': 1764966438,
            'cancel_at_period_end': False,
            'payment_method': {'brand': 'visa', 'last4': '4242'},
        },
        'customer_portal_url': 'string',
    }
    return OpenApiExample(
        name='Subscription state retrieved',
        value=value,
        status_codes=[200],
        description='Returns this response if the user has an active subscription',
    )


def stripe_error_response_example(code: int) -> OpenApiExample:
    return detail_response_example(name=f'Stripe {code} error', value='string', status_code=code)
