import pytest
from django.core.cache import cache

from core.apps.common.constants import CACHE_KEYS
from core.apps.payments.exceptions import StripeSubDoesNotExistError
from core.apps.payments.services.stripe_service import BaseStripeService
from core.apps.payments.use_cases.get_stripe_sub_state import GetStripeSubStateUseCase
from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser


@pytest.mark.django_db
def test_get_sub_state_error_raised_with_no_sub_state(
    get_sub_state_use_case_with_mocks: GetStripeSubStateUseCase,
    user: CustomUser,
):
    assert cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}') is None

    with pytest.raises(StripeSubDoesNotExistError):
        get_sub_state_use_case_with_mocks.execute(user=user_to_entity(user=user))


@pytest.mark.django_db
def test_get_sub_state_error_raised_with_sub_state_canceled(
    get_sub_state_use_case_with_mocks: GetStripeSubStateUseCase,
    stripe_service: BaseStripeService,
    user: CustomUser,
):
    expected_sub_state = {'status': 'canceled'}
    expected_customer_id = 'cus_123456789'

    assert cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}') is None
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') is None

    stripe_service.save_customer_id(user_id=user.pk, customer_id=expected_customer_id)
    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=expected_sub_state)

    assert cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}') == expected_customer_id
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') == expected_sub_state

    with pytest.raises(StripeSubDoesNotExistError):
        get_sub_state_use_case_with_mocks.execute(user=user_to_entity(user=user))


# FIXME: fix test
@pytest.mark.parametrize(
    argnames='expected_customer_id, expected_sub_status, expected_customer_portal_url',
    argvalues=[
        ('cus_123456789', 'active', 'https://example.com/customer_portal/12312i3u'),
        ('cus_218647826', 'trialing', 'https://example.com/customer_portal/saskgfjhghdgh'),
        ('cus_767265726', 'incomplete', 'https://example.com/customer_portal/ifghjogh034hg'),
        ('cus_111111111', 'incomplete_expired', 'https://example.com/customer_portal/f398uf3hdf'),
        ('cus_81272875', 'past_due', 'https://example.com/customer_portal/jshgjdhg'),
        ('cus_2425564', 'unpaid', 'https://example.com/customer_portal/p4ou9345'),
        ('cus_982759285', 'paused', 'https://example.com/customer_portal/bb49usdasf'),
    ],
)
@pytest.mark.django_db
def test_get_sub_state_error_raised_with_sub_state_active(
    get_sub_state_use_case_with_mocks: GetStripeSubStateUseCase,
    stripe_service: BaseStripeService,
    user: CustomUser,
    expected_customer_id: str,
    expected_sub_status: str,
    expected_customer_portal_url: str,
):
    expected_sub_state = {'status': expected_sub_status}
    get_sub_state_use_case_with_mocks.stripe_service.stripe_provider.expected_customer_portal_session_url = (
        expected_customer_portal_url
    )

    assert cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}') is None
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') is None

    stripe_service.save_customer_id(user_id=user.pk, customer_id=expected_customer_id)
    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=expected_sub_state)

    assert cache.get(f'{CACHE_KEYS["stripe_customer_id"]}{user.id}') == expected_customer_id
    assert cache.get(f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}') == expected_sub_state

    use_case_result: dict = get_sub_state_use_case_with_mocks.execute(user=user_to_entity(user=user))
    assert use_case_result['sub_state'] == expected_sub_state
    assert use_case_result['customer_portal_url'] == expected_customer_portal_url
