import random
from abc import (
    ABC,
    abstractmethod,
)

from django.core.cache import cache

from ..exceptions.codes import (
    CodeNotEqualException,
    CodeNotFoundException,
)


class BaseCodeService(ABC):
    @abstractmethod
    def generate_code(self): ...

    @abstractmethod
    def validate_code(self): ...


class EmailCodeService(BaseCodeService):
    _KEY_PREFIX = 'otp_code_'

    def generate_code(self, email: str) -> str:
        code = str(random.randint(100000, 999999))  # noqa
        cache.set(key=self._KEY_PREFIX + email, value=code, timeout=60 * 5)
        return code

    def validate_code(self, email: str, code: str) -> None:
        cached_code = cache.get(key=self._KEY_PREFIX + email)

        if cached_code is None:
            raise CodeNotFoundException()

        if cached_code != code:
            raise CodeNotEqualException(cached_code=cached_code, user_code=code)

        cache.delete(key=self._KEY_PREFIX + email)
