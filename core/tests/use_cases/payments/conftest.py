import punq
import pytest

from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from core.apps.users.use_cases.users.user_invalidate_stripe_cache import UserInvalidateStripeCacheUseCase


@pytest.fixture
def user_invalidate_stripe_cache_use_case(container: punq.Container) -> UserInvalidateStripeCacheUseCase:
    return container.resolve(UserInvalidateStripeCacheUseCase)


@pytest.fixture
def create_checkout_session_use_case(mock_container: punq.Container) -> CreateCheckoutSessionUseCase:
    return mock_container.resolve(CreateCheckoutSessionUseCase)
