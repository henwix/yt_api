import punq
import pytest

from core.apps.payments.services.stripe_service import (
    BaseCustomerIdValidatorService,
    BaseStripeEventValidatorService,
    BaseStripeService,
    BaseStripeSubAlreadyExistsValidatorService,
    BaseStripeSubDoesNotExistValidatorService,
    BaseStripeSubStillActiveValidatorService,
)
from core.tests.mocks.payments.stripe import DummyStripeService


@pytest.fixture
def stripe_service_with_dummy_provider(mock_container: punq.Container) -> BaseStripeService:
    return mock_container.resolve(BaseStripeService)


@pytest.fixture
def stripe_dummy_service_with_dummy_provider(mock_container: punq.Container) -> BaseStripeService:
    mock_container.register(BaseStripeService, DummyStripeService)
    return mock_container.resolve(BaseStripeService)


@pytest.fixture
def stripe_sub_still_active_validator_service(container: punq.Container) -> BaseStripeSubStillActiveValidatorService:
    return container.resolve(BaseStripeSubStillActiveValidatorService)


@pytest.fixture
def stripe_sub_does_not_exist_validator_service(container: punq.Container) -> BaseStripeSubDoesNotExistValidatorService:
    return container.resolve(BaseStripeSubDoesNotExistValidatorService)


@pytest.fixture
def stripe_sub_already_exists_validator_service(
    container: punq.Container,
) -> BaseStripeSubAlreadyExistsValidatorService:
    return container.resolve(BaseStripeSubAlreadyExistsValidatorService)


@pytest.fixture
def stripe_customer_id_validator_service(container: punq.Container) -> BaseCustomerIdValidatorService:
    return container.resolve(BaseCustomerIdValidatorService)


@pytest.fixture
def stripe_event_type_validator_service(container: punq.Container) -> BaseStripeEventValidatorService:
    return container.resolve(BaseStripeEventValidatorService)
