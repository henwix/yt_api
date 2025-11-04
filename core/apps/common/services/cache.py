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
    def get(self, key: str) -> Any: ...

    @abstractmethod
    def set(self, key: str, data: Any, timeout: int | None = None) -> bool: ...

    @abstractmethod
    def delete(self, key: str) -> bool: ...


@dataclass
class CacheService(BaseCacheService):
    def get(self, key: str) -> Any:
        return self.cache_provider.get(key)

    def set(self, key: str, data: Any, timeout: int | None = None) -> bool:
        return self.cache_provider.set(key, data, timeout)

    def delete(self, key: str) -> bool:
        return self.cache_provider.delete(key)
