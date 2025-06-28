from abc import (
    ABC,
    abstractmethod,
)
from typing import Any

from django.core.cache import cache


class BaseCacheProvider(ABC):
    @abstractmethod
    def get(self, key: str) -> Any:
        ...

    @abstractmethod
    def set(self, key: str, value: Any, timeout: int) -> None:
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        ...

    @abstractmethod
    def delete_keys(self, keys: list):
        ...

    @abstractmethod
    def delete_pattern(self, pattern: str) -> None:
        ...


class RedisCacheProvider(BaseCacheProvider):
    def get(self, key: str) -> Any:
        return cache.get(key)

    def set(self, key: str, value: Any, timeout: int) -> None:
        return cache.set(key, value, timeout)

    def delete(self, key: str) -> None:
        return cache.delete(key)

    def delete_keys(self, keys: list):
        cache.delete_many(keys)

    def delete_pattern(self, pattern: str) -> None:
        cache.delete_pattern(pattern)
