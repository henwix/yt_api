import random
import uuid
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from logging import Logger

from django.db.utils import settings

from core.apps.common.services.cache import BaseCacheService
from core.apps.users.entities import UserEntity
from core.apps.users.exceptions.codes import (
    OtpCodeNotEqualError,
    OtpCodeNotProvidedOrNotFoundError,
    ResetCodeNotEqualError,
    ResetCodeNotNotFoundError,
    SetEmailCodeNotProvidedOrNotFoundError,
    SetEmailUserNotEqualError,
)


class BaseCodeService(ABC):
    @abstractmethod
    def generate_email_otp_code(self, email: str) -> str:
        ...

    @abstractmethod
    def validate_email_otp_code(self, email: str, code: str | None) -> None:
        ...

    @abstractmethod
    def generate_set_email_code(self, user_id: int, email: str) -> str:
        ...

    @abstractmethod
    def validate_set_email_code(self, user_id: int, code: str) -> str:
        ...

    @abstractmethod
    def generate_user_email_code(self, user: UserEntity, cache_prefix: str) -> str:
        ...

    @abstractmethod
    def validate_user_email_code(self, user: UserEntity, code: str, cache_prefix: str) -> bool:
        ...


@dataclass
class EmailCodeService(BaseCodeService):
    logger: Logger
    cache_service: BaseCacheService

    _OTP_CACHE_KEY_PREFIX = settings.CACHE_KEYS.get('otp_email')
    _SET_EMAIL_CACHE_KEY_PREFIX = settings.CACHE_KEYS.get('set_email')

    def generate_email_otp_code(self, email: str) -> str:
        code = str(random.randint(100000, 999999))  # noqa
        self.cache_service.cache_data(key=self._OTP_CACHE_KEY_PREFIX + email, data=code, timeout=60 * 5)
        return code

    def validate_email_otp_code(self, email: str, code: str | None) -> None:
        cached_code = self.cache_service.get_cached_data(key=self._OTP_CACHE_KEY_PREFIX + email)

        if cached_code is None:
            raise OtpCodeNotProvidedOrNotFoundError(email=email)

        if cached_code != code:
            raise OtpCodeNotEqualError(cached_code=cached_code, user_code=code)

        self.cache_service.delete_cached_data(key=self._OTP_CACHE_KEY_PREFIX + email)

    def generate_set_email_code(self, user_id: int, email: str) -> str:
        code = uuid.uuid4().hex

        self.cache_service.cache_data(
            key=self._SET_EMAIL_CACHE_KEY_PREFIX + code,
            data={'user_id': user_id, 'new_email': email},
            timeout=60 * 5,
        )

        return code

    def validate_set_email_code(self, user_id: int, code: str) -> str:
        cache_key = self._SET_EMAIL_CACHE_KEY_PREFIX + code
        cached_data = self.cache_service.get_cached_data(key=cache_key)

        if cached_data is None:
            raise SetEmailCodeNotProvidedOrNotFoundError(user_id=user_id, user_code=code)

        if cached_data.get('user_id') != user_id:
            raise SetEmailUserNotEqualError(user_id=user_id, cached_user_id=cached_data.get('user_id'))

        self.cache_service.delete_cached_data(key=cache_key)

        return cached_data.get('new_email')

    def generate_user_email_code(self, user: UserEntity, cache_prefix: str) -> str:
        code = uuid.uuid4().hex

        self.cache_service.cache_data(
            key=f'{cache_prefix}{user.id}',
            data=code,
            timeout=60 * 5,
        )

        return code

    def validate_user_email_code(self, user: UserEntity, code: str, cache_prefix: str) -> bool:
        cache_key = f'{cache_prefix}{user.id}'
        cached_code = self.cache_service.get_cached_data(key=cache_key)

        if cached_code is None:
            raise ResetCodeNotNotFoundError(user_id=user.id, code=code)

        if code != cached_code:
            raise ResetCodeNotEqualError(user_id=user.id, code=code)

        self.cache_service.delete_cached_data(key=cache_key)

        return True
