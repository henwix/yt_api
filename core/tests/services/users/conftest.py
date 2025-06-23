import punq
import pytest

from core.apps.users.services.users import BaseUserService


@pytest.fixture
def user_service(container: punq.Container) -> BaseUserService:
    return container.resolve(BaseUserService)
