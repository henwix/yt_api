import punq
import pytest

from core.apps.users.use_cases.users.user_create import UserCreateUseCase


@pytest.fixture
def user_create_use_case(mock_container: punq.Container) -> UserCreateUseCase:
    return mock_container.resolve(UserCreateUseCase)
