import pytest
from django.core.cache import cache

from core.apps.common.constants import CACHE_KEYS
from core.apps.payments.exceptions import StripeInvalidSubTierError, StripeSubAlreadyExistsError
from core.apps.payments.services.stripe_service import BaseStripeService
from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser


@pytest.mark.parametrize(
    argnames='expected_url, expected_sub_tier, expected_customer_id',
    argvalues=[
        ('https://example.com/checkout_url/1231242552', 'pro', 'cus_123456789'),
        ('https://example.com/checkout_url/829929839823', 'premium', 'cus_218647826'),
        ('https://example.com/checkout_url/asfjkhsafk10', 'pro', 'cus_767265726'),
        ('https://example.com/checkout_url/929299292922', 'premium', 'cus_111111111'),
    ],
)
@pytest.mark.django_db
def test_checkout_session_created_with_existing_sub_state_canceled(
    stripe_service: BaseStripeService,
    create_checkout_session_use_case_with_mocks: CreateCheckoutSessionUseCase,
    user: CustomUser,
    expected_url: str,
    expected_sub_tier: str,
    expected_customer_id: str,
):
    expected_sub_state = {'status': 'canceled'}
    create_checkout_session_use_case_with_mocks.stripe_service.stripe_provider.expected_checkout_session_url = (
        expected_url
    )
    stripe_service.save_customer_id(user_id=user.id, customer_id=expected_customer_id)
    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=expected_sub_state)

    assert expected_customer_id == cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}')
    assert expected_sub_state == cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}')

    use_case_result = create_checkout_session_use_case_with_mocks.execute(
        sub_tier=expected_sub_tier, user=user_to_entity(user=user)
    )

    assert use_case_result == expected_url
    assert expected_customer_id == cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}')
    assert expected_sub_state == cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}')


@pytest.mark.parametrize(
    argnames='expected_sub_tier, expected_customer_id, expected_sub_status',
    argvalues=[
        ('pro', 'cus_123456789', 'active'),
        ('premium', 'cus_218647826', 'trialing'),
        ('pro', 'cus_767265726', 'incomplete'),
        ('premium', 'cus_111111111', 'incomplete_expired'),
        ('pro', 'cus_81272875', 'past_due'),
        ('premium', 'cus_2425564', 'unpaid'),
        ('pro', 'cus_982759285', 'paused'),
    ],
)
@pytest.mark.django_db
def test_checkout_session_error_raised_with_existing_sub_state_and_active_status(
    stripe_service: BaseStripeService,
    create_checkout_session_use_case_with_mocks: CreateCheckoutSessionUseCase,
    user: CustomUser,
    expected_sub_tier: str,
    expected_customer_id: str,
    expected_sub_status: str,
):
    expected_sub_state = {'status': expected_sub_status, 'customer_id': expected_customer_id}
    stripe_service.save_customer_id(user_id=user.id, customer_id=expected_customer_id)
    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=expected_sub_state)

    with pytest.raises(StripeSubAlreadyExistsError):
        create_checkout_session_use_case_with_mocks.execute(sub_tier=expected_sub_tier, user=user_to_entity(user=user))


@pytest.mark.parametrize(
    argnames='expected_sub_tier, expected_customer_id',
    argvalues=[
        ('test_tier', 'cus_123456789'),
        ('alskjfsaf', 'cus_218647826'),
        (123, 'cus_767265726'),
        (999, 'cus_111111111'),
        (('123', '456'), 'cus_81272875'),
        ('95835', 'cus_2425564'),
        ('hello_world', 'cus_982759285'),
    ],
)
@pytest.mark.django_db
def test_checkout_session_error_raised_with_wrong_sub_tier(
    stripe_service: BaseStripeService,
    create_checkout_session_use_case_with_mocks: CreateCheckoutSessionUseCase,
    user: CustomUser,
    expected_sub_tier: str,
    expected_customer_id: str,
):
    expected_sub_state = {'status': 'canceled', 'customer_id': expected_customer_id}
    stripe_service.save_customer_id(user_id=user.id, customer_id=expected_customer_id)
    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=expected_sub_state)

    with pytest.raises(StripeInvalidSubTierError):
        create_checkout_session_use_case_with_mocks.execute(sub_tier=expected_sub_tier, user=user_to_entity(user=user))


@pytest.mark.parametrize(
    argnames='expected_url, expected_sub_tier, expected_customer_id',
    argvalues=[
        ('https://example.com/checkout_url/1231242552', 'pro', 'cus_123456789'),
        ('https://example.com/checkout_url/829929839823', 'premium', 'cus_218647826'),
        ('https://example.com/checkout_url/asfjkhsafk10', 'pro', 'cus_767265726'),
        ('https://example.com/checkout_url/929299292922', 'premium', 'cus_111111111'),
    ],
)
@pytest.mark.django_db
def test_checkout_session_created_with_no_sub_state(
    create_checkout_session_use_case_with_mocks: CreateCheckoutSessionUseCase,
    user: CustomUser,
    expected_url: str,
    expected_sub_tier: str,
    expected_customer_id: str,
):
    create_checkout_session_use_case_with_mocks.stripe_service.stripe_provider.expected_checkout_session_url = (
        expected_url
    )
    create_checkout_session_use_case_with_mocks.stripe_service.stripe_provider.expected_customer_id = (
        expected_customer_id
    )

    assert cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}') is None
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') is None

    use_case_result = create_checkout_session_use_case_with_mocks.execute(
        sub_tier=expected_sub_tier, user=user_to_entity(user=user)
    )

    assert use_case_result == expected_url
    assert expected_customer_id == cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}')
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') is None
