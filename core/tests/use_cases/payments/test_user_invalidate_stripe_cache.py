from django.core.cache import cache

from core.apps.common.constants import CACHE_KEYS
from core.apps.payments.services.stripe_service import BaseStripeService
from core.apps.users.use_cases.users.user_invalidate_stripe_cache import UserInvalidateStripeCacheUseCase


def test_user_stripe_cache_not_invalidated_if_not_exists(
    user_invalidate_stripe_cache_use_case: UserInvalidateStripeCacheUseCase,
):
    user_invalidate_stripe_cache_use_case.execute(user_id=1)


def test_user_stripe_cache_invalidated(
    user_invalidate_stripe_cache_use_case: UserInvalidateStripeCacheUseCase,
    stripe_service: BaseStripeService,
):
    expected_user_id = 10
    expected_customer_id = 'cus_12534535'
    expected_sub_state = {'status': 'active'}
    customer_id_cache_key = f'{CACHE_KEYS["stripe_customer_id"]}{expected_user_id}'
    sub_state_cache_key = f'{CACHE_KEYS["stripe_sub_state"]}{expected_customer_id}'

    assert cache.get(customer_id_cache_key) is None
    assert cache.get(sub_state_cache_key) is None

    stripe_service.save_customer_id(expected_user_id, customer_id=expected_customer_id)
    stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, state=expected_sub_state)
    assert cache.get(customer_id_cache_key) == expected_customer_id
    assert cache.get(sub_state_cache_key) == expected_sub_state

    user_invalidate_stripe_cache_use_case.execute(user_id=expected_user_id)
    assert cache.get(customer_id_cache_key) is None
    assert cache.get(sub_state_cache_key) is None
