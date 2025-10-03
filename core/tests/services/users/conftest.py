import punq
import pytest

from core.apps.users.services.users import (
    BaseUserActivatedValidatorService,
    BaseUserActivationRequiredValidatorService,
    BaseUserService,
)


@pytest.fixture
def user_service(container: punq.Container) -> BaseUserService:
    return container.resolve(BaseUserService)


@pytest.fixture
def user_activation_required_validator_service(container: punq.Container) -> BaseUserActivationRequiredValidatorService:
    return container.resolve(BaseUserActivationRequiredValidatorService)


@pytest.fixture
def user_activated_validator_service(container: punq.Container) -> BaseUserActivatedValidatorService:
    return container.resolve(BaseUserActivatedValidatorService)
