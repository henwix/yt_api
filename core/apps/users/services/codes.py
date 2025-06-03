import random
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from logging import Logger

from core.apps.common.providers.cache import BaseCacheProvider
from core.apps.users.exceptions.codes import (
    CodeNotEqualException,
    CodeNotProvidedException,
)


class BaseCodeService(ABC):
    @abstractmethod
    def generate_code(self, email: str) -> str:
        ...

    @abstractmethod
    def validate_code(self, email: str, code: str | None) -> None:
        ...


@dataclass
class EmailCodeService(BaseCodeService):
    logger: Logger
    cache_provider: BaseCacheProvider

    _KEY_PREFIX = 'otp_code_'

    def generate_code(self, email: str) -> str:
        code = str(random.randint(100000, 999999))  # noqa
        self.cache_provider.set(key=self._KEY_PREFIX + email, value=code, timeout=60 * 5)
        return code

    def validate_code(self, email: str, code: str | None) -> None:
        cached_code = self.cache_provider.get(key=self._KEY_PREFIX + email)

        if cached_code is None:
            raise CodeNotProvidedException(email=email)

        if cached_code != code:
            raise CodeNotEqualException(cached_code=cached_code, user_code=code)

        self.cache_provider.delete(key=self._KEY_PREFIX + email)
