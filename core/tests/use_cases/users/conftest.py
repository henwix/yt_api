import punq
import pytest

from core.apps.users.use_cases.users.user_create import UserCreateUseCase
from core.apps.users.use_cases.users.user_set_email import UserSetEmailUseCase
from core.apps.users.use_cases.users.user_set_password import UserSetPasswordUseCase


@pytest.fixture
def user_create_use_case(mock_container: punq.Container) -> UserCreateUseCase:
    return mock_container.resolve(UserCreateUseCase)


@pytest.fixture
def user_set_password_use_case(mock_container: punq.Container) -> UserSetPasswordUseCase:
    return mock_container.resolve(UserSetPasswordUseCase)


@pytest.fixture
def user_set_email_use_case(mock_container: punq.Container) -> UserSetEmailUseCase:
    return mock_container.resolve(UserSetEmailUseCase)
