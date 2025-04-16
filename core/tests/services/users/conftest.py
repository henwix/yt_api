import pytest
from punq import Container

from core.apps.users.services.users import BaseUserService


@pytest.fixture
def user_service(container: Container):
    return container.resolve(BaseUserService)
