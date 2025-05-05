import random
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from logging import Logger

from core.apps.common.providers.cache import BaseCacheProvider

from ..exceptions.codes import (
    CodeNotEqualException,
    CodeNotFoundException,
)


class BaseCodeService(ABC):
    @abstractmethod
    def generate_code(self): ...

    @abstractmethod
    def validate_code(self): ...


@dataclass
class EmailCodeService(BaseCodeService):
    logger: Logger
    cache_provider: BaseCacheProvider

    _KEY_PREFIX = 'otp_code_'

    def generate_code(self, email: str) -> str:
        code = str(random.randint(100000, 999999))  # noqa
        self.cache_provider.set(key=self._KEY_PREFIX + email, value=code, timeout=60 * 5)
        return code

    def validate_code(self, email: str, code: str) -> None:
        cached_code = self.cache_provider.get(key=self._KEY_PREFIX + email)

        if cached_code is None:
            raise CodeNotFoundException(email=email)

        if cached_code != code:
            raise CodeNotEqualException(cached_code=cached_code, user_code=code)

        self.cache_provider.delete(key=self._KEY_PREFIX + email)
