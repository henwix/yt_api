import random
from abc import ABC

from django.core.cache import cache

from ..exceptions.codes import (
    CodeNotEqualException,
    CodeNotFoundException,
)


class BaseCodeService(ABC):
    def generate_code(self): ...

    def validate_code(self): ...


class EmailCodeService(BaseCodeService):
    def generate_code(self, email):
        code = random.randint(100000, 999999)  # noqa
        cache.set(email, code, 60 * 5)
        return code

    def validate_code(self, email, code):
        cached_code = cache.get(email)

        if cached_code is None:
            raise CodeNotFoundException()

        if cached_code != code:
            raise CodeNotEqualException(cached_code=cached_code, user_code=code)

        cache.delete(email)
