import punq
import pytest

from core.apps.users.services.codes import BaseCodeService


@pytest.fixture
def code_service(container: punq.Container) -> BaseCodeService:
    return container.resolve(BaseCodeService)
