import uuid
from typing import Any

import pytest
from django.core.cache import cache

from core.apps.common.constants import CACHE_KEYS
from core.apps.payments.enums import (
    StripeSubscriptionAllTiersEnum,
    StripeSubscriptionPaidTiersEnum,
    StripeSubscriptionStatusesEnum,
)
from core.apps.payments.exceptions import (
    StripeCustomerIdNotStringError,
    StripeInvalidSubPriceError,
    StripeInvalidSubTierError,
    StripeNotAllowedEventTypeError,
    StripeSubAlreadyExistsError,
    StripeSubDoesNotExistError,
    StripeSubStillActiveError,
)
from core.apps.payments.services.stripe_service import (
    BaseCustomerIdValidatorService,
    BaseStripeEventValidatorService,
    BaseStripeService,
    BaseStripeSubAlreadyExistsValidatorService,
    BaseStripeSubDoesNotExistValidatorService,
    BaseStripeSubStillActiveValidatorService,
)
from core.apps.users.converters.users import user_to_entity
from core.apps.users.entities import AnonymousUserEntity
from core.apps.users.models import CustomUser


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
def test_sub_state_saved(
    stripe_service: BaseStripeService, expected_sub_id: str, expected_price_id: str, expected_customer_id: str
):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'
    expected_sub_state = {'subscription_id': expected_sub_id, 'price_id': expected_price_id}

    assert cache.get(sub_state_cache_key) is None

    is_saved = stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=expected_sub_state)
    assert is_saved is True
    assert cache.get(sub_state_cache_key) == expected_sub_state


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

    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=expected_sub_state)

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

    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=expected_sub_state)

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
    argnames='expected_customer_id, expected_sub_tier',
    argvalues=(
        ['cus_123456789', StripeSubscriptionPaidTiersEnum.PRO],
        ['cus_987654321', StripeSubscriptionPaidTiersEnum.PREMIUM],
        ['cus_767265726', StripeSubscriptionPaidTiersEnum.PRO],
        ['cus_756275622', StripeSubscriptionPaidTiersEnum.PREMIUM],
    ),
)
def test_sub_state_updated_if_never_exists_before(
    stripe_dummy_service_with_dummy_provider: BaseStripeService,
    dummy_stripe_sub_object: dict,
    expected_customer_id: str,
    expected_sub_tier: str,
):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'
    stripe_dummy_service_with_dummy_provider.get_sub_tier_by_sub_price_response = expected_sub_tier

    saved_sub = stripe_dummy_service_with_dummy_provider.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert saved_sub is None
    assert cache.get(sub_state_cache_key) is None

    is_updated = stripe_dummy_service_with_dummy_provider.update_customer_sub_state(
        customer_id=expected_customer_id, sub=dummy_stripe_sub_object
    )
    assert is_updated is True

    saved_sub = stripe_dummy_service_with_dummy_provider.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert cache.get(sub_state_cache_key) == saved_sub
    assert saved_sub['subscription_id'] == dummy_stripe_sub_object['id']
    assert saved_sub['customer_id'] == expected_customer_id
    assert saved_sub['status'] == dummy_stripe_sub_object['status']
    assert saved_sub['price_id'] == dummy_stripe_sub_object['items']['data'][0]['price']['id']
    assert saved_sub['tier'] == expected_sub_tier
    assert saved_sub['current_period_start'] == dummy_stripe_sub_object['items']['data'][0]['current_period_start']
    assert saved_sub['current_period_end'] == dummy_stripe_sub_object['items']['data'][0]['current_period_end']
    assert saved_sub['cancel_at_period_end'] == dummy_stripe_sub_object['cancel_at_period_end']
    assert saved_sub['payment_method'] is None


@pytest.mark.parametrize(
    argnames=[
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
        ['cus_918273645', 'pro', 'sub_746382223', 'trialing', False, '5532', 'price_192837465', 1736112000, 1738790400],
        ['cus_564738291', 'premium', 'sub_56438291', 'active', True, '9081', 'price_837261945', 1719792000, 1722470400],
        ['cus_837261945', 'pro', 'sub_92837455', 'incomplete', True, '6207', 'price_564738291', 1727827200, 1730505600],
        ['cus_217465', 'premium', 'sub_8102', 'incomplete_expired', True, '4740', 'price_3645', 1740960000, 1743638400],
        ['cus_6574820', 'premium', 'sub_01928346', 'past_due', False, '3951', 'price_46382910', 1725148800, 1727827200],
        ['cus_829102746', 'pro', 'sub_283746192', 'canceled', False, '7772', 'price_293847561', 1733088000, 1735766400],
        ['cus_374829102', 'premium', 'sub_91827645', 'unpaid', False, '8820', 'price_87261945', 1746307200, 1748899200],
        ['cus_546372819', 'pro', 'sub_192837465', 'paused', True, '1204', 'price_564738291', 1717200000, 1719878400],
    ),
)
def test_sub_state_updated_if_already_exists(
    stripe_dummy_service_with_dummy_provider: BaseStripeService,
    dummy_stripe_sub_object: dict,
    expected_customer_id: str,
    expected_sub_tier: str,
    expected_sub_id: str,
    expected_sub_status: str,
    expected_sub_cancel_at_period_end: bool,
    expected_sub_payment_method: str,
    expected_sub_price_id: str,
    expected_sub_current_period_start: int,
    expected_sub_current_period_end: int,
):
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'

    # save old sub state for customer
    stripe_dummy_service_with_dummy_provider.get_sub_tier_by_sub_price_response = 'pro'
    dummy_stripe_sub_object['id'] = expected_sub_id
    is_updated = stripe_dummy_service_with_dummy_provider.update_customer_sub_state(
        customer_id=expected_customer_id, sub=dummy_stripe_sub_object
    )
    assert is_updated is True

    # save new sub state for customer
    stripe_dummy_service_with_dummy_provider.get_sub_tier_by_sub_price_response = expected_sub_tier
    new_stripe_sub_object = {
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
    is_updated = stripe_dummy_service_with_dummy_provider.update_customer_sub_state(
        customer_id=expected_customer_id, sub=new_stripe_sub_object
    )
    assert is_updated is True

    saved_sub = stripe_dummy_service_with_dummy_provider.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert cache.get(sub_state_cache_key) == saved_sub
    assert saved_sub['subscription_id'] == new_stripe_sub_object['id']
    assert saved_sub['customer_id'] == expected_customer_id
    assert saved_sub['status'] == new_stripe_sub_object['status']
    assert saved_sub['price_id'] == new_stripe_sub_object['items']['data'][0]['price']['id']
    assert saved_sub['tier'] == expected_sub_tier
    assert saved_sub['current_period_start'] == new_stripe_sub_object['items']['data'][0]['current_period_start']
    assert saved_sub['current_period_end'] == new_stripe_sub_object['items']['data'][0]['current_period_end']
    assert saved_sub['cancel_at_period_end'] == new_stripe_sub_object['cancel_at_period_end']
    assert saved_sub['payment_method'] is None


@pytest.mark.parametrize(
    argnames='expected_sub_price, expected_customer_id, expected_user_id, expected_checkout_url',
    argvalues=[
        ('price_123456789', 'cus_123456789', 424, 'https://example.com/124987129847'),
        ('price_987654321', 'cus_218647826', 22, 'https://example.com/1892482748274'),
        ('price_767265726', 'cus_111111111', 4, 'https://example.com/asjfhakjsfh'),
    ],
)
def test_checkout_session_created(
    stripe_dummy_service_with_dummy_provider: BaseStripeService,
    expected_sub_price: str,
    expected_customer_id: str,
    expected_user_id: int,
    expected_checkout_url: str,
):
    stripe_dummy_service_with_dummy_provider.stripe_provider.expected_checkout_session_url = expected_checkout_url
    stripe_dummy_service_with_dummy_provider.get_sub_price_by_sub_tier_response = expected_sub_price

    session = stripe_dummy_service_with_dummy_provider.create_checkout_session(
        customer_id=expected_customer_id, user_id=expected_user_id, sub_tier=StripeSubscriptionPaidTiersEnum.PRO
    )

    assert expected_checkout_url == session.url


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
        customer_id=expected_customer_id, data={'tier': 'test', 'status': expected_sub_status}
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
        customer_id=expected_customer_id, data={'tier': expected_sub_tier, 'status': expected_sub_status}
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


@pytest.mark.django_db
def test_sub_still_active_validator_not_raised_with_canceled_status(
    stripe_service: BaseStripeService,
    stripe_sub_still_active_validator_service: BaseStripeSubStillActiveValidatorService,
    user: CustomUser,
):
    stripe_service.save_customer_id(user.pk, customer_id='cus_123456789')
    stripe_service.save_sub_state_by_customer_id(customer_id='cus_123456789', data={'status': 'canceled'})
    stripe_sub_still_active_validator_service.validate(user=user_to_entity(user=user))


@pytest.mark.django_db
def test_sub_still_active_validator_not_raised_with_no_state(
    stripe_sub_still_active_validator_service: BaseStripeSubStillActiveValidatorService,
    user: CustomUser,
):
    stripe_sub_still_active_validator_service.validate(user=user_to_entity(user=user))


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_status',
    argvalues=[
        'active',
        'trialing',
        'incomplete',
        'incomplete_expired',
        'past_due',
        'unpaid',
        'paused',
    ],
)
def test_sub_still_active_validator_raised_with_not_allowed_statuses(
    stripe_service: BaseStripeService,
    stripe_sub_still_active_validator_service: BaseStripeSubStillActiveValidatorService,
    user: CustomUser,
    expected_status: str,
):
    stripe_service.save_customer_id(user.pk, customer_id='cus_123456789')
    stripe_service.save_sub_state_by_customer_id(customer_id='cus_123456789', data={'status': expected_status})

    with pytest.raises(StripeSubStillActiveError):
        stripe_sub_still_active_validator_service.validate(user=user_to_entity(user=user))


@pytest.mark.parametrize(
    argnames='expected_status',
    argvalues=[
        'active',
        'trialing',
        'incomplete',
        'incomplete_expired',
        'past_due',
        'unpaid',
        'paused',
    ],
)
def test_does_not_exist_validator_not_raised_with_allowed_statuses(
    stripe_sub_does_not_exist_validator_service: BaseStripeSubDoesNotExistValidatorService,
    expected_status: str,
):
    stripe_sub_does_not_exist_validator_service.validate(sub={'status': expected_status})


def test_does_not_exist_validator_raised_with_no_state(
    stripe_sub_does_not_exist_validator_service: BaseStripeSubDoesNotExistValidatorService,
):
    with pytest.raises(StripeSubDoesNotExistError):
        stripe_sub_does_not_exist_validator_service.validate(sub=None)


def test_does_not_exist_validator_raised_with_canceled_status(
    stripe_sub_does_not_exist_validator_service: BaseStripeSubDoesNotExistValidatorService,
):
    with pytest.raises(StripeSubDoesNotExistError):
        stripe_sub_does_not_exist_validator_service.validate(sub={'status': 'canceled'})


def test_already_exists_validator_not_raised_with_canceled_status(
    stripe_sub_already_exists_validator_service: BaseStripeSubAlreadyExistsValidatorService,
):
    stripe_sub_already_exists_validator_service.validate(sub={'status': 'canceled'})


def test_already_exists_validator_not_raised_with_no_state(
    stripe_sub_already_exists_validator_service: BaseStripeSubAlreadyExistsValidatorService,
):
    stripe_sub_already_exists_validator_service.validate(sub=None)


@pytest.mark.parametrize(
    argnames='expected_status',
    argvalues=[
        'active',
        'trialing',
        'incomplete',
        'incomplete_expired',
        'past_due',
        'unpaid',
        'paused',
    ],
)
def test_already_exists_validator_raised_with_not_allowed_statuses(
    stripe_sub_already_exists_validator_service: BaseStripeSubAlreadyExistsValidatorService,
    expected_status: str,
):
    with pytest.raises(StripeSubAlreadyExistsError):
        stripe_sub_already_exists_validator_service.validate(sub={'status': expected_status, 'customer_id': 'cus_123'})


def test_customer_id_validator_not_raised_with_allowed_type(
    stripe_customer_id_validator_service: BaseCustomerIdValidatorService,
):
    stripe_customer_id_validator_service.validate(customer_id='cus_218647826')


@pytest.mark.parametrize('expected_customer_id', [[], {}, 123, ()])
def test_customer_id_validator_raised_with_not_allowed_type(
    stripe_customer_id_validator_service: BaseCustomerIdValidatorService,
    expected_customer_id: Any,
):
    with pytest.raises(StripeCustomerIdNotStringError):
        stripe_customer_id_validator_service.validate(customer_id=expected_customer_id)


@pytest.mark.parametrize(
    argnames='expected_event_type',
    argvalues=[
        'checkout.session.completed',
        'customer.subscription.created',
        'customer.subscription.updated',
        'customer.subscription.deleted',
        'customer.subscription.trial_will_end',
        'invoice.paid',
        'invoice.payment_failed',
        'payment_intent.payment_failed',
        'payment_intent.canceled',
    ],
)
def test_stripe_event_type_validator_not_raised_with_allowed_types(
    stripe_event_type_validator_service: BaseStripeEventValidatorService,
    expected_event_type: str,
):
    stripe_event_type_validator_service.validate(event={'type': expected_event_type})


def test_stripe_event_type_validator_raised_with_not_allowed_types(
    stripe_event_type_validator_service: BaseStripeEventValidatorService,
):
    with pytest.raises(StripeNotAllowedEventTypeError):
        stripe_event_type_validator_service.validate(event={'type': 'test.event_type'})
