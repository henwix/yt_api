import punq
import pytest

from core.apps.users.use_cases.users.auth_authorize import AuthorizeUserUseCase
from core.apps.users.use_cases.users.auth_verify_code import VerifyCodeUseCase


@pytest.fixture
def authorize_user_use_case(mock_container: punq.Container) -> AuthorizeUserUseCase:
    return mock_container.resolve(AuthorizeUserUseCase)


@pytest.fixture
def verify_code_use_case(container: punq.Container) -> VerifyCodeUseCase:
    return container.resolve(VerifyCodeUseCase)
