from abc import ABC, abstractmethod
from typing import Any

from django.core.cache import cache


class BaseCacheService(ABC):
    @abstractmethod
    def get_cached_data(self, key: str) -> Any: ...

    @abstractmethod
    def cache_data(self, key: str, data: Any, timeout: int) -> None: ...


class CacheService(BaseCacheService):
    def get_cached_data(self, key: str) -> Any:
        return cache.get(key)

    def cache_data(self, key: str, data: Any, timeout: int) -> None:
        return cache.set(key, data, timeout)
