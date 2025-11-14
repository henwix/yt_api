import uuid
from typing import Any

import pytest
import stripe
from django.core.cache import cache

from core.apps.common.constants import CACHE_KEYS
from core.apps.payments.enums import (
    StripeSubscriptionAllTiersEnum,
    StripeSubscriptionPaidTiersEnum,
    StripeSubscriptionStatusesEnum,
)
from core.apps.payments.exceptions import (
    StripeInvalidSubPriceError,
    StripeInvalidSubTierError,
)
from core.apps.payments.services.stripe_service import (
    BaseStripeService,
)
from core.apps.users.converters.users import user_to_entity
from core.apps.users.entities import AnonymousUserEntity
from core.apps.users.models import CustomUser
from core.tests.conftest import make_stripe_pm


@pytest.mark.parametrize(
    argnames='expected_customer_id, expected_user_id',
    argvalues=[('cus_123456789', 152), ('cus_987654321', 946), ('cus_111111111', 42384), ('cus_218647826', 27)],
)
def test_customer_id_saved(stripe_service: BaseStripeService, expected_customer_id: str, expected_user_id: int):
    customer_id_cache_key = f'{CACHE_KEYS["stripe_customer_id"]}{expected_user_id}'

    assert cache.get(customer_id_cache_key) is None

    is_saved = stripe_service.save_customer_id(user_id=expected_user_id, customer_id=expected_customer_id)
    assert is_saved is True
    assert cache.get(customer_id_cache_key) == expected_customer_id


@pytest.mark.parametrize(
    argnames='expected_customer_id, expected_user_id',
    argvalues=[('cus_123456789', 152), ('cus_987654321', 946), ('cus_111111111', 42384), ('cus_218647826', 27)],
)
def test_customer_id_retrieved(stripe_service: BaseStripeService, expected_customer_id: str, expected_user_id: int):
    customer_id_cache_key = f'{CACHE_KEYS["stripe_customer_id"]}{expected_user_id}'

    stripe_service.save_customer_id(user_id=expected_user_id, customer_id=expected_customer_id)

    saved_customer_id = stripe_service.get_customer_id(user_id=expected_user_id)
    assert cache.get(customer_id_cache_key) == saved_customer_id
    assert saved_customer_id == expected_customer_id


@pytest.mark.parametrize('expected_user_id', [1, 13, 146, 4265])
def test_get_customer_id_returns_none_when_not_found(stripe_service: BaseStripeService, expected_user_id: int):
    customer_id_cache_key = f'{CACHE_KEYS["stripe_customer_id"]}{expected_user_id}'

    customer_id = stripe_service.get_customer_id(user_id=expected_user_id)
    assert customer_id is None
    assert cache.get(customer_id_cache_key) is None


@pytest.mark.parametrize(
    argnames='expected_customer_id, expected_user_id',
    argvalues=[('cus_123456789', 152), ('cus_987654321', 946), ('cus_111111111', 42384), ('cus_218647826', 27)],
)
def test_customer_id_deleted(stripe_service: BaseStripeService, expected_customer_id: str, expected_user_id: int):
    customer_id_cache_key = f'{CACHE_KEYS["stripe_customer_id"]}{expected_user_id}'
    stripe_service.save_customer_id(user_id=expected_user_id, customer_id=expected_customer_id)
    assert cache.get(customer_id_cache_key) == expected_customer_id

    is_deleted = stripe_service.delete_customer_id(expected_user_id)
    assert is_deleted is True

    assert cache.get(customer_id_cache_key) is None

    saved_customer_id = stripe_service.get_customer_id(user_id=expected_user_id)
    assert saved_customer_id is None


@pytest.mark.parametrize(
    argnames='expected_user_id',
    argvalues=[0, 5, 14, 463, 55522, 924829],
)
def test_delete_customer_id_returns_false_if_not_exists(stripe_service: BaseStripeService, expected_user_id: int):
    customer_id_cache_key = f'{CACHE_KEYS["stripe_customer_id"]}{expected_user_id}'
    assert cache.get(customer_id_cache_key) is None

    is_deleted = stripe_service.delete_customer_id(expected_user_id)
    assert is_deleted is False

    assert cache.get(customer_id_cache_key) is None

    saved_customer_id = stripe_service.get_customer_id(user_id=expected_user_id)
    assert saved_customer_id is None


@pytest.mark.parametrize(
    argnames='expected_sub_id, expected_price_id, expected_customer_id',
    argvalues=[
        ('sub_123456789', 'price_123456789', 'cus_123456789'),
        ('sub_987654321', 'price_987654321', 'cus_987654321'),
        ('sub_676378562', 'price_264728978', 'cus_172846278'),
    ],
)
def test_sub_state_saved_if_never_existed_before(
    stripe_service: BaseStripeService, expected_sub_id: str, expected_price_id: str, expected_customer_id: str
):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'
    expected_sub_state = {'subscription_id': expected_sub_id, 'price_id': expected_price_id}

    assert cache.get(sub_state_cache_key) is None

    is_saved = stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, state=expected_sub_state)
    assert is_saved is True
    assert cache.get(sub_state_cache_key) == expected_sub_state


@pytest.mark.parametrize(
    argnames=[
        'expected_old_sub_id',
        'expected_new_sub_id',
        'expected_old_price_id',
        'expected_new_price_id',
        'expected_customer_id',
    ],
    argvalues=[
        ('sub_123456789', 'sub_987654321', 'price_123456789', 'price_987654321', 'cus_123456789'),
        ('sub_232482647', 'sub_287467246', 'price_462746242', 'price_887248262', 'cus_987654321'),
        ('sub_781287472', 'sub_222959589', 'price_921398293', 'price_123726444', 'cus_928497444'),
    ],
)
def test_sub_state_saved_if_already_exists(
    stripe_service: BaseStripeService,
    expected_old_sub_id: str,
    expected_new_sub_id: str,
    expected_old_price_id: str,
    expected_new_price_id: str,
    expected_customer_id: str,
):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'
    expected_old_sub_state = {'subscription_id': expected_old_sub_id, 'price_id': expected_old_price_id}
    expected_new_sub_state = {'subscription_id': expected_new_sub_id, 'price_id': expected_new_price_id}

    assert cache.get(sub_state_cache_key) is None

    # save first time
    is_saved = stripe_service.save_sub_state_by_customer_id(
        customer_id=expected_customer_id, state=expected_old_sub_state
    )
    assert is_saved is True
    assert cache.get(sub_state_cache_key) == expected_old_sub_state

    # save second time
    is_saved = stripe_service.save_sub_state_by_customer_id(
        customer_id=expected_customer_id, state=expected_new_sub_state
    )
    assert is_saved is True
    assert cache.get(sub_state_cache_key) == expected_new_sub_state


@pytest.mark.parametrize(
    argnames='expected_sub_id, expected_price_id, expected_customer_id',
    argvalues=[
        ('sub_123456789', 'price_123456789', 'cus_123456789'),
        ('sub_987654321', 'price_987654321', 'cus_987654321'),
        ('sub_676378562', 'price_264728978', 'cus_172846278'),
    ],
)
def test_sub_state_retrieved(
    stripe_service: BaseStripeService, expected_sub_id: str, expected_price_id: str, expected_customer_id: str
):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'
    expected_sub_state = {'subscription_id': expected_sub_id, 'price_id': expected_price_id}

    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, state=expected_sub_state)

    saved_sub_state = stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert cache.get(sub_state_cache_key) == saved_sub_state
    assert saved_sub_state == expected_sub_state


@pytest.mark.parametrize('expected_customer_id', ['cus_123456789', 'cus_987654321', 'cus_767265726'])
def test_get_sub_state_returns_none_when_not_found(stripe_service: BaseStripeService, expected_customer_id: str):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'

    assert cache.get(sub_state_cache_key) is None

    sub_state = stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert cache.get(sub_state_cache_key) is None
    assert sub_state is None


def test_get_sub_state_returns_none_when_not_found_without_customer_id(stripe_service: BaseStripeService):
    sub_state = stripe_service.get_sub_state_by_customer_id(customer_id=None)
    assert sub_state is None


@pytest.mark.parametrize(
    argnames='expected_sub_id, expected_price_id, expected_customer_id',
    argvalues=[
        ('sub_123456789', 'price_123456789', 'cus_123456789'),
        ('sub_987654321', 'price_987654321', 'cus_987654321'),
        ('sub_676378562', 'price_264728978', 'cus_172846278'),
    ],
)
def test_sub_state_deleted(
    stripe_service: BaseStripeService, expected_sub_id: str, expected_price_id: str, expected_customer_id: str
):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'
    expected_sub_state = {'subscription_id': expected_sub_id, 'price_id': expected_price_id}

    assert cache.get(sub_state_cache_key) is None

    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, state=expected_sub_state)

    assert cache.get(sub_state_cache_key) == expected_sub_state

    is_deleted = stripe_service.delete_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert is_deleted is True

    assert cache.get(sub_state_cache_key) is None

    saved_sub_state = stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert saved_sub_state is None


@pytest.mark.parametrize('expected_customer_id', ['cus_123456789', 'cus_987654321', 'cus_767265726'])
def test_delete_sub_state_returns_false_if_not_exists(stripe_service: BaseStripeService, expected_customer_id: str):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'

    assert cache.get(sub_state_cache_key) is None
    is_deleted = stripe_service.delete_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert is_deleted is False
    assert cache.get(sub_state_cache_key) is None


@pytest.mark.parametrize(
    argnames='expected_customer_id, expected_sub_tier, dummy_stripe_sub_object',
    argvalues=(
        ['cus_123', 'pro', {'default_payment_method': 'pm_123'}],
        ['cus_987', 'premium', {'default_payment_method': 'pm_456'}],
        ['cus_767', 'pro', {'default_payment_method': 'pm_789'}],
        ['cus_756', 'premium', {'default_payment_method': 'pm_248'}],
    ),
    indirect=['dummy_stripe_sub_object'],
)
def test_build_sub_state_with_stripe_pm_id_as_payment_method(
    stripe_dummy_service_with_dummy_provider: BaseStripeService,
    dummy_stripe_sub_object: stripe.Subscription,
    expected_customer_id: str,
    expected_sub_tier: str,
):
    """
    If the payment method is passed as a string (ID) instead of a Stripe PaymentMethod object, the subscription state
    must set 'default_payment_method' field to None
    """
    stripe_dummy_service_with_dummy_provider.get_sub_tier_by_sub_price_response = expected_sub_tier
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

    build_state = stripe_dummy_service_with_dummy_provider.build_sub_state(
        customer_id=expected_customer_id, sub=dummy_stripe_sub_object
    )
    assert expected_sub_state == build_state


@pytest.mark.parametrize(
    argnames='expected_customer_id, expected_sub_tier, default_pm',
    argvalues=(
        ['cus_123', 'pro', make_stripe_pm('card', {'brand': 'visa', 'last4': '4242'})],
        ['cus_987', 'premium', make_stripe_pm('ideal', {'bank': 'testbank'})],
        ['cus_767', 'pro', make_stripe_pm('link', {'email': 'user@example.com'})],
        ['cus_756', 'premium', make_stripe_pm('us_bank_account', {'last4': '6789', 'bank_name': 'STRIPE TEST BANK'})],
        # add some test fields for the pm object that should not be used in the sub state building method
        ['cus_982', 'pro', make_stripe_pm('card', {'test_field_1': '456', 'test_field_2': '123'})],
        ['cus_255', 'premium', make_stripe_pm('ideal', {'test_field_3': 'aaa', 'test_field_4': 'askdj'})],
    ),
)
def test_build_sub_state_with_stripe_pm_object_as_payment_method(
    stripe_dummy_service_with_dummy_provider: BaseStripeService,
    dummy_stripe_sub_object: stripe.Subscription,
    expected_customer_id: str,
    expected_sub_tier: str,
    default_pm: stripe.PaymentMethod,
):
    """
    If a Stripe PaymentMethod object is passed, the subscription state must be built using its attributes, and
    'default_payment_method' must contain the extracted data
    """
    stripe_dummy_service_with_dummy_provider.get_sub_tier_by_sub_price_response = expected_sub_tier
    dummy_stripe_sub_object['default_payment_method'] = default_pm
    default_pm_type = default_pm['type']
    expected_sub_state = {
        'subscription_id': dummy_stripe_sub_object['id'],
        'customer_id': expected_customer_id,
        'status': dummy_stripe_sub_object['status'],
        'price_id': dummy_stripe_sub_object['items']['data'][0]['price']['id'],
        'tier': expected_sub_tier,
        'current_period_start': dummy_stripe_sub_object['items']['data'][0]['current_period_start'],
        'current_period_end': dummy_stripe_sub_object['items']['data'][0]['current_period_end'],
        'cancel_at_period_end': dummy_stripe_sub_object['cancel_at_period_end'],
        'payment_method': {
            'type': default_pm_type,
            'brand': default_pm[default_pm_type].get('brand'),
            'last4': default_pm[default_pm_type].get('last4'),
            'bank': default_pm[default_pm_type].get('bank'),
            'bank_name': default_pm[default_pm_type].get('bank_name'),
            'email': default_pm[default_pm_type].get('email'),
        },
    }

    build_state = stripe_dummy_service_with_dummy_provider.build_sub_state(
        customer_id=expected_customer_id, sub=dummy_stripe_sub_object
    )
    assert expected_sub_state == build_state


@pytest.mark.parametrize(
    argnames='expected_sub_price, expected_customer_id, expected_user_id, expected_trial_days, expected_checkout_url',
    argvalues=[
        ('price_123456789', 'cus_123456789', 424, None, 'https://example.com/124987129847'),
        ('price_987654321', 'cus_218647826', 22, 14, 'https://example.com/1892482748274'),
        ('price_767265726', 'cus_111111111', 4, 5, 'https://example.com/asjfhakjsfh'),
        ('price_767265726', 'cus_111111111', 4, None, 'https://example.com/asjfhakjsfh'),
    ],
)
def test_checkout_session_created(
    stripe_dummy_service_with_dummy_provider: BaseStripeService,
    expected_sub_price: str,
    expected_customer_id: str,
    expected_user_id: int,
    expected_trial_days: int | None,
    expected_checkout_url: str,
):
    stripe_dummy_service_with_dummy_provider.stripe_provider.expected_checkout_session_url = expected_checkout_url
    stripe_dummy_service_with_dummy_provider.get_sub_price_by_sub_tier_response = expected_sub_price

    session = stripe_dummy_service_with_dummy_provider.create_checkout_session(
        customer_id=expected_customer_id,
        user_id=expected_user_id,
        sub_tier=StripeSubscriptionPaidTiersEnum.PRO,
        trial_days=expected_trial_days,
    )

    assert expected_checkout_url == session.url
    assert expected_customer_id == session.customer_id
    assert expected_user_id == session.user_id
    assert expected_sub_price == session.sub_price
    assert 'auto' == session.billing_address_collection
    assert expected_trial_days == session.trial_days


@pytest.mark.parametrize(
    argnames='expected_user_id, expected_email, expected_customer_id',
    argvalues=[
        (582, 'HrV7E@example.com', 'cus_767265726'),
        (15, 'Ql8qM@example.com', 'cus_246824244'),
        (24591, 'example@example.com', 'cus_111111111'),
    ],
)
def test_customer_created(
    stripe_service_with_dummy_provider: BaseStripeService,
    expected_user_id: int,
    expected_email: str,
    expected_customer_id: str,
):
    stripe_service_with_dummy_provider.stripe_provider.expected_customer_id = expected_customer_id

    customer = stripe_service_with_dummy_provider.create_customer(email=expected_email, user_id=expected_user_id)

    assert customer.id == expected_customer_id
    assert customer.email == expected_email
    assert customer.user_id == expected_user_id


@pytest.mark.parametrize(
    argnames='expected_sub_tier, expected_sub_price',
    argvalues=[
        ('pro', 'price_000488284'),
        ('medium', 'price_8782578275'),
        ('premium', 'price_444444444'),
        ('basic', 'price_2819191225'),
        ('advanced', 'price_9999992222'),
    ],
)
def test_sub_price_retrieved_by_sub_tier(
    stripe_service: BaseStripeService, expected_sub_tier: str, expected_sub_price: str
):
    stripe_service._STRIPE_SUBSCRIPTION_TIER_PRICES = {expected_sub_tier: expected_sub_price}

    retrieved_sub_price = stripe_service.get_sub_price_by_sub_tier(sub_tier=expected_sub_tier)
    assert expected_sub_price == retrieved_sub_price


def test_get_sub_price_by_sub_tier_invalid_tier_error(stripe_service: BaseStripeService):
    stripe_service._STRIPE_SUBSCRIPTION_TIER_PRICES = {}

    with pytest.raises(StripeInvalidSubTierError):
        stripe_service.get_sub_price_by_sub_tier(sub_tier='unknown')


@pytest.mark.parametrize(
    argnames='expected_sub_tier, expected_sub_price',
    argvalues=[
        ('pro', 'price_000488284'),
        ('medium', 'price_8782578275'),
        ('premium', 'price_444444444'),
        ('basic', 'price_2819191225'),
        ('advanced', 'price_9999992222'),
    ],
)
def test_sub_tier_retrieved_by_sub_price(
    stripe_service: BaseStripeService, expected_sub_tier: str, expected_sub_price: str
):
    stripe_service._STRIPE_SUBSCRIPTION_TIER_PRICES_INVERTED = {expected_sub_price: expected_sub_tier}

    retrieved_sub_tier = stripe_service.get_sub_tier_by_sub_price(sub_price=expected_sub_price)
    assert expected_sub_tier == retrieved_sub_tier


def test_get_sub_tier_by_sub_price_invalid_price_error(stripe_service: BaseStripeService):
    stripe_service._STRIPE_SUBSCRIPTION_TIER_PRICES_INVERTED = {}

    with pytest.raises(StripeInvalidSubPriceError):
        stripe_service.get_sub_tier_by_sub_price(sub_price='unknown')


def test_sub_tier_retrieved_for_anonymous_user(stripe_service: BaseStripeService):
    retrieved_sub_tier = stripe_service.get_sub_tier_by_user(user=AnonymousUserEntity())
    assert retrieved_sub_tier == StripeSubscriptionAllTiersEnum.FREE


@pytest.mark.django_db
def test_sub_tier_retrieved_for_user_with_no_sub_state(stripe_service: BaseStripeService, user: CustomUser):
    retrieved_sub_tier = stripe_service.get_sub_tier_by_user(user=user_to_entity(user=user))
    assert retrieved_sub_tier == StripeSubscriptionAllTiersEnum.FREE


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_sub_status',
    argvalues=[
        StripeSubscriptionStatusesEnum.INCOMPLETE,
        StripeSubscriptionStatusesEnum.INCOMPLETE_EXPIRED,
        StripeSubscriptionStatusesEnum.PAST_DUE,
        StripeSubscriptionStatusesEnum.CANCELED,
        StripeSubscriptionStatusesEnum.UNPAID,
        StripeSubscriptionStatusesEnum.PAUSED,
    ],
)
def test_sub_tier_retrieved_and_status_is_not_active_or_trialing(
    stripe_service: BaseStripeService, user: CustomUser, expected_sub_status: str
):
    expected_customer_id = 'cus_123456789'
    stripe_service.save_customer_id(user.pk, customer_id=expected_customer_id)
    stripe_service.save_sub_state_by_customer_id(
        customer_id=expected_customer_id, state={'tier': 'test', 'status': expected_sub_status}
    )

    retrieved_sub_tier = stripe_service.get_sub_tier_by_user(user=user_to_entity(user=user))
    assert retrieved_sub_tier == StripeSubscriptionAllTiersEnum.FREE


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_sub_tier, expected_sub_status',
    argvalues=[
        ('pro', StripeSubscriptionStatusesEnum.ACTIVE),
        ('premium', StripeSubscriptionStatusesEnum.ACTIVE),
        ('basic', StripeSubscriptionStatusesEnum.ACTIVE),
        ('advanced', StripeSubscriptionStatusesEnum.ACTIVE),
        ('pro', StripeSubscriptionStatusesEnum.TRIALING),
        ('premium', StripeSubscriptionStatusesEnum.TRIALING),
        ('basic', StripeSubscriptionStatusesEnum.TRIALING),
        ('advanced', StripeSubscriptionStatusesEnum.TRIALING),
    ],
)
def test_sub_tier_retrieved_with_active_and_trialing_status(
    stripe_service: BaseStripeService, user: CustomUser, expected_sub_tier: str, expected_sub_status: str
):
    expected_customer_id = 'cus_123456789'
    stripe_service.save_customer_id(user.pk, customer_id=expected_customer_id)
    stripe_service.save_sub_state_by_customer_id(
        customer_id=expected_customer_id, state={'tier': expected_sub_tier, 'status': expected_sub_status}
    )

    retrieved_sub_tier = stripe_service.get_sub_tier_by_user(user=user_to_entity(user=user))
    assert retrieved_sub_tier == expected_sub_tier


def test_subs_list_retrieved(stripe_service_with_dummy_provider: BaseStripeService):
    expected_customer_id = 'cus_123456789'

    subs_retrieved = stripe_service_with_dummy_provider.get_subs_list_by_customer_id(customer_id=expected_customer_id)
    assert subs_retrieved.status == 'all'
    assert subs_retrieved.customer_id == expected_customer_id
    assert subs_retrieved.limit == 1
    assert subs_retrieved.expand == ['data.default_payment_method']


@pytest.mark.parametrize(
    argnames='expected_payload, expected_signature', argvalues=[('1234', '5678'), ('qwert', 'yuiop')]
)
def test_event_constructed(
    stripe_service_with_dummy_provider: BaseStripeService, expected_payload: str, expected_signature: str
):
    retrieved_event = stripe_service_with_dummy_provider.construct_event(
        payload=expected_payload, signature=expected_signature
    )

    assert expected_payload == retrieved_event['payload']
    assert expected_signature == retrieved_event['signature']


@pytest.mark.parametrize(argnames='expected_customer_id', argvalues=['cus_724242525', 'cus_111111111', 'cus_246824244'])
def test_portal_session_url_retrieved_and_cached(
    stripe_service_with_dummy_provider: BaseStripeService, expected_customer_id: str
):
    # Prepare a unique expected URL that will be returned and cached by the service
    expected_cached_portal_session_url = f'https://example.com/portal_session/{uuid.uuid4()}/'
    stripe_service_with_dummy_provider.stripe_provider.expected_customer_portal_session_url = (
        expected_cached_portal_session_url
    )

    # Verify that the Stripe provider hasn’t been called yet
    assert stripe_service_with_dummy_provider.stripe_provider.customer_portal_session_url_call_count == 0

    # Call the service method (this should invoke the provider and cache the result)
    retrieved_portal_session_url = stripe_service_with_dummy_provider.get_customer_portal_session_url(
        customer_id=expected_customer_id
    )
    assert retrieved_portal_session_url == expected_cached_portal_session_url

    # The provider should only be called once because the value is now cached
    assert stripe_service_with_dummy_provider.stripe_provider.customer_portal_session_url_call_count == 1

    # Call the service multiple times to verify caching behavior
    for _ in range(10):
        # Change the provider’s expected return value to ensure the cache is actually used
        new_portal_session_url = f'https://example.com/portal_session/{uuid.uuid4()}/'
        stripe_service_with_dummy_provider.stripe_provider.expected_customer_portal_session_url = new_portal_session_url

        # Retrieve the value again — should still return the cached one
        retrieved_portal_session_url = stripe_service_with_dummy_provider.get_customer_portal_session_url(
            customer_id=expected_customer_id
        )

        # Assert that the cached value was returned and the new one was ignored
        assert retrieved_portal_session_url == expected_cached_portal_session_url
        assert retrieved_portal_session_url != new_portal_session_url

        # Verify that the provider was still called only once (cache hit)
        assert stripe_service_with_dummy_provider.stripe_provider.customer_portal_session_url_call_count == 1


def test_trial_days_retrieved_with_no_sub_data(stripe_service: BaseStripeService):
    """Test that the method returns the correct trail_days value if no sub_state was provided"""
    expected_trial_days = 7
    assert stripe_service.get_sub_trial_days() == expected_trial_days


def test_trial_days_returns_none_with_sub_data(stripe_service: BaseStripeService):
    """Test that the method returns None if sub state was provided"""
    assert stripe_service.get_sub_trial_days(sub_state={'status': 'canceled'}) is None


@pytest.mark.parametrize('expected_pm', ['pm_123456789', 123, None, ['123', '456'], (1, 2)])
def test_sub_state_extracted_without_stripe_pm_object(stripe_service: BaseStripeService, expected_pm: Any):
    assert stripe_service.extract_sub_payment_method_info(pm=expected_pm) is None


@pytest.mark.parametrize(
    argnames='expected_pm',
    argvalues=[
        make_stripe_pm('card', {'brand': 'amex', 'last4': '4242', 'country': 'TestCountry', 'exp_year': 2027}),
        make_stripe_pm(
            'card', {'brand': 'mastercard', 'last4': '4351', 'funding': 'debit', 'regulated_status': 'regulated'}
        ),
        make_stripe_pm('card_present', {'brand': 'visa', 'last4': '1111', 'brand_product': 'K1', 'country': 'USA'}),
        make_stripe_pm('card_present', {'brand': 'mastercard', 'last4': '2222', 'exp_month': 11, 'issuer': 'test'}),
        make_stripe_pm(
            'us_bank_account',
            {
                'bank_name': 'STRIPE TEST BANK',
                'last4': '6789',
                'account_holder_type': 'individual',
                'routing_number': '110000000',
            },
        ),
        make_stripe_pm(
            'us_bank_account',
            {
                'bank_name': 'TEST NATIONAL BANK',
                'last4': '9876',
                'account_type': 'savings',
                'routing_number': '120000000',
            },
        ),
        make_stripe_pm(
            'sepa_debit', {'branch_code': '1234kasfjaf', 'last4': '1300', 'country': 'DE', 'bank_code': '37040044'}
        ),
        make_stripe_pm('sepa_debit', {'branch_code': 'ALK', 'last4': '4521', 'country': 'NL', 'bank_code': 'INGBNL2A'}),
        make_stripe_pm('bacs_debit', {'last4': '0000', 'sort_code': '10-20-30', 'fingerprint': 'rJ7hT0Ha8w2xjeF6'}),
        make_stripe_pm('bacs_debit', {'last4': '3333', 'sort_code': '20-30-40', 'fingerprint': 'aF3kL7Hw0ZpXk2Q9'}),
        make_stripe_pm('au_becs_debit', {'last4': '1234', 'bsb_number': '082-000', 'fingerprint': 'Fg4hT0Jb9Yy8kX1L'}),
        make_stripe_pm('au_becs_debit', {'last4': '5678', 'bsb_number': '092-000', 'fingerprint': 'Bq2mW5Tz7KfL1V8J'}),
        make_stripe_pm('ideal', {'bic': 'INGBNL2A', 'bank_code': 'ING'}),
        make_stripe_pm('ideal', {'bic': 'RABONL2U', 'bank_code': 'RABO'}),
        make_stripe_pm('sofort', {'country': 'AT'}),
        make_stripe_pm('sofort', {'country': 'DE'}),
        make_stripe_pm('eps', {'bank': 'helloworld_bank', 'bic': 'SPKRAT2P', 'bank_code': 'SPKRAT2P'}),
        make_stripe_pm('eps', {'bank': '123_456_bank', 'bic': 'GIBAATWWXXX', 'bank_code': 'ERSTATWW'}),
        make_stripe_pm('bancontact', {'bank': 'bank_7424224', 'swift': 'KREDBEBB', 'bank_code': 'KREDBEBB'}),
        make_stripe_pm('bancontact', {'swift': 'INGBNL2A', 'bank_code': 'INGBNL2A'}),
        make_stripe_pm('giropay', {'bank': 'asd_bank', 'bank_code': '37040044', 'bic': 'GENODEF1VN'}),
        make_stripe_pm('giropay', {'bank_code': '37010050', 'bic': 'PBNKDEFF'}),
        make_stripe_pm('link', {'email': 'user@example.com'}),
        make_stripe_pm('link', {'email': 'another_user@example.com'}),
        make_stripe_pm('klarna', {'email': 'klarna_user@example.com', 'dob': {'day': 15, 'month': 4, 'year': 1985}}),
        make_stripe_pm('klarna', {'dob': {'day': 30, 'month': 10, 'year': 1990}}),
        make_stripe_pm('afterpay_clearpay', {'email': 'after@test.com', 'billing_details_email': 'after@test.com'}),
        make_stripe_pm('afterpay_clearpay', {'billing_details_email': 'customer@example.com'}),
        make_stripe_pm('alipay', {'billing_details_email': 'alipay_user@example.com'}),
        make_stripe_pm('alipay', {'email': 'pay_user@example.com', 'billing_details_email': 'pay_user@example.com'}),
        make_stripe_pm(
            'grabpay',
            {'bank': 'grabpay', 'bank_name': 'grabpay_bank', 'billing_details_email': 'grab_user@example.com'},
        ),
        make_stripe_pm('grabpay', {'bank': 'maybank_123', 'billing_details_email': 'maybank_user@example.com'}),
        make_stripe_pm('paynow', {'bank': 'DBS', 'billing_details_email': 'paynow_user@example.com'}),
        make_stripe_pm('paynow', {'bank': 'OCBC', 'billing_details_email': 'ocbc_user@example.com'}),
    ],
)
def test_sub_state_extracted_with_stripe_pm_object(
    stripe_service: BaseStripeService,
    expected_pm: stripe.PaymentMethod,
):
    pm_type = expected_pm['type']
    pm_data = expected_pm[pm_type]
    expected_pm = {
        'type': pm_type,
        'brand': pm_data.get('brand'),
        'last4': pm_data.get('last4'),
        'bank': pm_data.get('bank'),
        'bank_name': pm_data.get('bank_name'),
        'email': pm_data.get('email'),
    }
    assert stripe_service.extract_sub_payment_method_info(pm=expected_pm) is None
