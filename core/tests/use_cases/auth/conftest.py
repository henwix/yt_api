import punq
import pytest

from core.apps.users.use_cases.auth import (
    AuthorizeUserUseCase,
    VerifyCodeUseCase,
)


@pytest.fixture
def authorize_user_use_case(mock_container: punq.Container) -> AuthorizeUserUseCase:
    return mock_container.resolve(AuthorizeUserUseCase)


@pytest.fixture
def verify_code_use_case(container: punq.Container) -> VerifyCodeUseCase:
    return container.resolve(VerifyCodeUseCase)
