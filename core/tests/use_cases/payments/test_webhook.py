import pytest
import stripe
from django.core.cache import cache

from core.apps.common.constants import CACHE_KEYS
from core.apps.payments.services.stripe_service import BaseStripeService
from core.apps.payments.use_cases.webhook import StripeWebhookUseCase
from core.tests.conftest import make_stripe_pm


@pytest.mark.parametrize(
    argnames=[
        'expected_event_type',
        'expected_customer_id',
        'expected_sub_tier',
        'dummy_stripe_sub_object',
    ],
    argvalues=(
        [
            'checkout.session.completed',
            'cus_918273645',
            'pro',
            {
                'id': 'sub_746382223',
                'status': 'trialing',
                'cancel_at_period_end': False,
                'default_payment_method': 'pm_5874284724',
                'price_id': 'price_192837465',
                'current_period_start': 1736112000,
                'current_period_end': 1738790400,
            },
        ],
        [
            'customer.subscription.created',
            'cus_564738291',
            'premium',
            {
                'id': 'sub_56438291',
                'status': 'active',
                'cancel_at_period_end': True,
                'default_payment_method': make_stripe_pm(
                    'us_bank_account', {'test_123_field_2': 'askja', 'test_field_1': '123'}
                ),
                'price_id': 'price_837261945',
                'current_period_start': 1719792000,
                'current_period_end': 1722470400,
            },
        ],
        [
            'customer.subscription.updated',
            'cus_837261945',
            'pro',
            {
                'id': 'sub_92837455',
                'status': 'incomplete',
                'cancel_at_period_end': True,
                'default_payment_method': make_stripe_pm('card', {'last4': '5544', 'brand': 'mastercard'}),
                'price_id': 'price_564738291',
                'current_period_start': 1727827200,
                'current_period_end': 1730505600,
            },
        ],
        [
            'customer.subscription.deleted',
            'cus_217465',
            'premium',
            {
                'id': 'sub_8102',
                'status': 'incomplete_expired',
                'cancel_at_period_end': True,
                'default_payment_method': make_stripe_pm('card', {'last4': '1234', 'brand': 'testercard'}),
                'price_id': 'price_3645',
                'current_period_start': 1740960000,
                'current_period_end': 1743638400,
            },
        ],
        [
            'customer.subscription.trial_will_end',
            'cus_6574820',
            'premium',
            {
                'id': 'sub_01928346',
                'status': 'past_due',
                'cancel_at_period_end': False,
                'default_payment_method': make_stripe_pm('link', {'email': 'user@example.com'}),
                'price_id': 'price_46382910',
                'current_period_start': 1725148800,
                'current_period_end': 1727827200,
            },
        ],
        [
            'invoice.paid',
            'cus_829102746',
            'pro',
            {
                'id': 'sub_283746192',
                'status': 'canceled',
                'cancel_at_period_end': False,
                'default_payment_method': make_stripe_pm(
                    'us_bank_account', {'last4': '8242', 'bank': 'test bank', 'bank_name': 'STRIPE TEST BANK'}
                ),
                'price_id': 'price_293847561',
                'current_period_start': 1733088000,
                'current_period_end': 1735766400,
            },
        ],
        [
            'invoice.payment_failed',
            'cus_374829102',
            'premium',
            {
                'id': 'sub_91827645',
                'status': 'unpaid',
                'cancel_at_period_end': False,
                'default_payment_method': make_stripe_pm('exp', {'bank': 'test_bank_123'}),
                'price_id': 'price_87261945',
                'current_period_start': 1746307200,
                'current_period_end': 1748899200,
            },
        ],
        [
            'payment_intent.payment_failed',
            'cus_546372819',
            'pro',
            {
                'id': 'sub_192837465',
                'status': 'paused',
                'cancel_at_period_end': True,
                'default_payment_method': make_stripe_pm(
                    'us_bank_account', {'bank': 'hellworld', 'bank_name': 'hellworld bank'}
                ),
                'price_id': 'price_564738291',
                'current_period_start': 1717200000,
                'current_period_end': 1719878400,
            },
        ],
        [
            'payment_intent.canceled',
            'cus_982592582',
            'premium',
            {
                'id': 'sub_192837465',
                'status': 'paused',
                'cancel_at_period_end': True,
                'default_payment_method': make_stripe_pm('card', {'last4': '4242', 'brand': 'visa'}),
                'price_id': 'price_564738291',
                'current_period_start': 1717200000,
                'current_period_end': 1719878400,
            },
        ],
    ),
    indirect=['dummy_stripe_sub_object'],
)
def test_webhook_sub_state_updated(
    webhook_use_case_with_mock_service_and_provider: StripeWebhookUseCase,
    stripe_service: BaseStripeService,
    expected_event_type: str,
    expected_customer_id: str,
    expected_sub_tier: str,
    dummy_stripe_sub_object: stripe.Subscription,
):
    expected_sub_state = {
        'subscription_id': dummy_stripe_sub_object['id'],
        'customer_id': expected_customer_id,
        'status': dummy_stripe_sub_object['status'],
        'price_id': dummy_stripe_sub_object['items']['data'][0]['price']['id'],
        'tier': expected_sub_tier,
        'current_period_start': dummy_stripe_sub_object['items']['data'][0]['current_period_start'],
        'current_period_end': dummy_stripe_sub_object['items']['data'][0]['current_period_end'],
        'cancel_at_period_end': dummy_stripe_sub_object['cancel_at_period_end'],
        'payment_method': None,
    }

    if isinstance(dummy_stripe_sub_object['default_payment_method'], stripe.PaymentMethod):
        pm_type = dummy_stripe_sub_object['default_payment_method'].get('type')
        pm_data: dict = dummy_stripe_sub_object['default_payment_method'].get(pm_type, {})

        expected_sub_state['payment_method'] = {
            'type': pm_type,
            'brand': pm_data.get('brand'),
            'last4': pm_data.get('last4'),
            'bank': pm_data.get('bank'),
            'bank_name': pm_data.get('bank_name'),
            'email': pm_data.get('email'),
        }

    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.expected_event_type = (
        expected_event_type
    )
    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.expected_customer_id = (
        expected_customer_id
    )
    webhook_use_case_with_mock_service_and_provider.stripe_service.stripe_provider.stripe_subs_data = [
        dummy_stripe_sub_object
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
