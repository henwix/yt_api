import punq
import pytest

from core.apps.common.services.encoding import BaseEncodingService


@pytest.fixture
def encoding_service(container: punq.Container) -> BaseEncodingService:
    return container.resolve(BaseEncodingService)
