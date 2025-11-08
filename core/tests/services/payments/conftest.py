import punq
import pytest

from core.apps.payments.enums import StripeSubscriptionStatusesEnum
from core.apps.payments.services.stripe_service import BaseStripeService
from core.tests.mocks.payments.stripe import DummyStripeService


@pytest.fixture
def stripe_service(container: punq.Container) -> BaseStripeService:
    return container.resolve(BaseStripeService)


@pytest.fixture
def stripe_service_with_dummy_provider(mock_container: punq.Container) -> BaseStripeService:
    return mock_container.resolve(BaseStripeService)


@pytest.fixture
def stripe_dummy_service_with_dummy_provider(mock_container: punq.Container) -> BaseStripeService:
    mock_container.register(BaseStripeService, DummyStripeService)
    return mock_container.resolve(BaseStripeService)


@pytest.fixture
def dummy_stripe_subscription() -> dict:
    return {
        'id': 'sub_123456789',
        'status': StripeSubscriptionStatusesEnum.ACTIVE,
        'cancel_at_period_end': False,
        'default_payment_method': '123',
        'items': {
            'data': [
                {
                    'price': {
                        'id': 'price_123456789',
                    },
                    'current_period_start': 1762366397,
                    'current_period_end': 1764958397,
                },
            ],
        },
    }
