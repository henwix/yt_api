import punq
import pytest

from core.apps.common.services.cache import BaseCacheService


@pytest.fixture
def cache_service(container: punq.Container) -> BaseCacheService:
    return container.resolve(BaseCacheService)
