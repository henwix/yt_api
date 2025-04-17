from django.contrib.auth import get_user_model

import punq
import pytest

from core.apps.users.services.users import BaseUserService
from core.tests.factories.channels import UserModelFactory


User = get_user_model()


@pytest.fixture
def user_service(container: punq.Container) -> BaseUserService:
    return container.resolve(BaseUserService)


@pytest.fixture
def user() -> User:
    return UserModelFactory()
