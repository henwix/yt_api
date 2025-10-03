import punq
import pytest

from core.apps.users.use_cases.users.user_activation import UserActivationUseCase
from core.apps.users.use_cases.users.user_create import UserCreateUseCase
from core.apps.users.use_cases.users.user_resend_activation import UserResendActivationUseCase
from core.apps.users.use_cases.users.user_reset_password import UserResetPasswordUseCase
from core.apps.users.use_cases.users.user_reset_password_confirm import UserResetPasswordConfirmUseCase
from core.apps.users.use_cases.users.user_reset_username import UserResetUsernameUseCase
from core.apps.users.use_cases.users.user_reset_username_confirm import UserResetUsernameConfirmUseCase
from core.apps.users.use_cases.users.user_set_email import UserSetEmailUseCase
from core.apps.users.use_cases.users.user_set_email_confirm import UserSetEmailConfirmUseCase
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


@pytest.fixture
def user_set_email_confirm_use_case(mock_container: punq.Container) -> UserSetEmailConfirmUseCase:
    return mock_container.resolve(UserSetEmailConfirmUseCase)


@pytest.fixture
def user_reset_password_use_case(mock_container: punq.Container) -> UserResetPasswordUseCase:
    return mock_container.resolve(UserResetPasswordUseCase)


@pytest.fixture
def user_reset_password_confirm_use_case(mock_container: punq.Container) -> UserResetPasswordConfirmUseCase:
    return mock_container.resolve(UserResetPasswordConfirmUseCase)


@pytest.fixture
def user_reset_username_use_case(mock_container: punq.Container) -> UserResetUsernameUseCase:
    return mock_container.resolve(UserResetUsernameUseCase)


@pytest.fixture
def user_reset_username_confirm_use_case(mock_container: punq.Container) -> UserResetUsernameConfirmUseCase:
    return mock_container.resolve(UserResetUsernameConfirmUseCase)


@pytest.fixture
def user_activation_use_case(mock_container: punq.Container) -> UserActivationUseCase:
    return mock_container.resolve(UserActivationUseCase)


@pytest.fixture
def user_resend_activation_use_case(mock_container: punq.Container) -> UserResendActivationUseCase:
    return mock_container.resolve(UserResendActivationUseCase)
