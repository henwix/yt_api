import punq
import pytest

from core.apps.payments.services.stripe_service import BaseStripeService
from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from core.apps.payments.use_cases.get_stripe_sub_state import GetStripeSubStateUseCase
from core.apps.payments.use_cases.webhook import StripeWebhookUseCase
from core.apps.users.use_cases.users.user_invalidate_stripe_cache import UserInvalidateStripeCacheUseCase
from core.tests.mocks.payments.stripe import DummyStripeService


@pytest.fixture
def user_invalidate_stripe_cache_use_case(container: punq.Container) -> UserInvalidateStripeCacheUseCase:
    return container.resolve(UserInvalidateStripeCacheUseCase)


@pytest.fixture
def create_checkout_session_use_case_with_mocks(mock_container: punq.Container) -> CreateCheckoutSessionUseCase:
    return mock_container.resolve(CreateCheckoutSessionUseCase)


@pytest.fixture
def get_sub_state_use_case_with_mocks(mock_container: punq.Container) -> GetStripeSubStateUseCase:
    return mock_container.resolve(GetStripeSubStateUseCase)


@pytest.fixture
def webhook_use_case_with_mock_provider(mock_container: punq.Container) -> StripeWebhookUseCase:
    return mock_container.resolve(StripeWebhookUseCase)


@pytest.fixture
def webhook_use_case_with_mock_service_and_provider(mock_container: punq.Container) -> StripeWebhookUseCase:
    mock_container.register(BaseStripeService, DummyStripeService)
    return mock_container.resolve(StripeWebhookUseCase)
