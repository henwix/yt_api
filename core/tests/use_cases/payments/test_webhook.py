import pytest
from django.core.cache import cache

from core.apps.common.constants import CACHE_KEYS
from core.apps.payments.services.stripe_service import BaseStripeService
from core.apps.payments.use_cases.webhook import StripeWebhookUseCase


@pytest.mark.parametrize(
    argnames=[
        'expected_event_type',
        'expected_customer_id',
        'expected_sub_tier',
        'expected_sub_id',
        'expected_sub_status',
        'expected_sub_cancel_at_period_end',
        'expected_sub_payment_method',
        'expected_sub_price_id',
        'expected_sub_current_period_start',
        'expected_sub_current_period_end',
    ],
    argvalues=(
        [
            'checkout.session.completed',
            'cus_918273645',
            'pro',
            'sub_746382223',
            'trialing',
            False,
            '5532',
            'price_192837465',
            1736112000,
            1738790400,
        ],
        [
            'customer.subscription.created',
            'cus_564738291',
            'premium',
            'sub_56438291',
            'active',
            True,
            '9081',
            'price_837261945',
            1719792000,
            1722470400,
        ],
        [
            'customer.subscription.updated',
            'cus_837261945',
            'pro',
            'sub_92837455',
            'incomplete',
            True,
            '6207',
            'price_564738291',
            1727827200,
            1730505600,
        ],
        [
            'customer.subscription.deleted',
            'cus_217465',
            'premium',
            'sub_8102',
            'incomplete_expired',
            True,
            '4740',
            'price_3645',
            1740960000,
            1743638400,
        ],
        [
            'customer.subscription.trial_will_end',
            'cus_6574820',
            'premium',
            'sub_01928346',
            'past_due',
            False,
            '3951',
            'price_46382910',
            1725148800,
            1727827200,
        ],
        [
            'invoice.paid',
            'cus_829102746',
            'pro',
            'sub_283746192',
            'canceled',
            False,
            '7772',
            'price_293847561',
            1733088000,
            1735766400,
        ],
        [
            'invoice.payment_failed',
            'cus_374829102',
            'premium',
            'sub_91827645',
            'unpaid',
            False,
            '8820',
            'price_87261945',
            1746307200,
            1748899200,
        ],
        [
            'payment_intent.payment_failed',
            'cus_546372819',
            'pro',
            'sub_192837465',
            'paused',
            True,
            '1204',
            'price_564738291',
            1717200000,
            1719878400,
        ],
        [
            'payment_intent.canceled',
            'cus_982592582',
            'premium',
            'sub_192837465',
            'paused',
            True,
            '2555',
            'price_564738291',
            1717200000,
            1719878400,
        ],
    ),
)
def test_webhook_sub_state_updated(
    webhook_use_case_with_mock_service_and_provider: StripeWebhookUseCase,
    stripe_service: BaseStripeService,
    expected_event_type: str,
    expected_customer_id: str,
    expected_sub_id: str,
    expected_sub_tier: str,
    expected_sub_status: str,
    expected_sub_cancel_at_period_end: bool,
    expected_sub_payment_method: str,
    expected_sub_price_id: str,
    expected_sub_current_period_start: int,
    expected_sub_current_period_end: int,
):
    stripe_sub_object = {
        'id': expected_sub_id,
        'status': expected_sub_status,
        'cancel_at_period_end': expected_sub_cancel_at_period_end,
        'default_payment_method': expected_sub_payment_method,
        'items': {
            'data': [
                {
                    'price': {'id': expected_sub_price_id},
                    'current_period_start': expected_sub_current_period_start,
                    'current_period_end': expected_sub_current_period_end,
                },
            ],
        },
    }
    expected_sub_state = {
        'subscription_id': expected_sub_id,
        'customer_id': expected_customer_id,
        'status': expected_sub_status,
        'price_id': expected_sub_price_id,
        'tier': expected_sub_tier,
        'current_period_start': expected_sub_current_period_start,
        'current_period_end': expected_sub_current_period_end,
        'cancel_at_period_end': expected_sub_cancel_at_period_end,
        'payment_method': None,
    }

    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.expected_event_type = (
        expected_event_type
    )
    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.expected_customer_id = (
        expected_customer_id
    )
    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.stripe_subs_data = [
        stripe_sub_object
    ]
    webhook_use_case_with_mock_service_and_provider.stripe_service.get_sub_tier_by_sub_price_response = (
        expected_sub_tier
    )

    assert stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id) is None
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') is None

    webhook_use_case_with_mock_service_and_provider.execute(payload='123', signature='456')

    assert expected_sub_state == stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert expected_sub_state == cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}')


def test_webhook_sub_state_updated_with_no_subs(
    webhook_use_case_with_mock_service_and_provider: StripeWebhookUseCase,
    stripe_service: BaseStripeService,
):
    expected_customer_id = 'cus_374829102'
    expected_sub_state = {'status': 'canceled', 'customer_id': expected_customer_id}
    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.expected_event_type = (
        'payment_intent.canceled'
    )
    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.expected_customer_id = (
        expected_customer_id
    )
    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.stripe_subs_data = []

    assert stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id) is None
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') is None

    webhook_use_case_with_mock_service_and_provider.execute(payload='123', signature='456')

    assert stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id) == expected_sub_state
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') == expected_sub_state
