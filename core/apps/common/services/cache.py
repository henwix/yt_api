from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Any

from core.apps.common.providers.cache import BaseCacheProvider


@dataclass
class BaseCacheService(ABC):
    cache_provider: BaseCacheProvider

    @abstractmethod
    def get_cached_data(self, key: str) -> Any:
        ...

    @abstractmethod
    def cache_data(self, key: str, data: Any, timeout: int) -> None:
        ...

    @abstractmethod
    def delete_cached_data(self, key: str) -> None:
        ...


@dataclass
class CacheService(BaseCacheService):
    def get_cached_data(self, key: str) -> Any:
        return self.cache_provider.get(key)

    def cache_data(self, key: str, data: Any, timeout: int) -> None:
        return self.cache_provider.set(key, data, timeout)

    def delete_cached_data(self, key: str) -> None:
        return self.cache_provider.delete(key)
