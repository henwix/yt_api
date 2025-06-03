from abc import (
    ABC,
    abstractmethod,
)

from django.contrib.auth import authenticate

from core.apps.users.converters.users import user_to_entity
from core.apps.users.entities import UserEntity
from core.apps.users.models import CustomUser


class BaseUserRepository(ABC):
    @abstractmethod
    def authenticate(self, login: str, password: str) -> UserEntity | None:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        ...


class ORMUserRepository(BaseUserRepository):
    def authenticate(self, login: str, password: str) -> UserEntity | None:
        user_dto = authenticate(username=login, password=password)
        return user_to_entity(user_dto) if user_dto else None

    def get_by_email(self, email: str) -> UserEntity | None:
        user_dto = CustomUser.objects.filter(email=email).first()
        return user_to_entity(user_dto) if user_dto else None
