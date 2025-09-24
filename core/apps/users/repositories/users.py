from abc import (
    ABC,
    abstractmethod,
)

from django.contrib.auth import authenticate

from core.apps.users.converters.users import (
    user_from_entity,
    user_to_entity,
)
from core.apps.users.entities import UserEntity
from core.apps.users.models import CustomUser


class BaseUserRepository(ABC):
    @abstractmethod
    def authenticate(self, login: str, password: str) -> UserEntity | None:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> UserEntity | None:
        ...

    @abstractmethod
    def create_by_data(self, data: dict) -> CustomUser:
        ...

    @abstractmethod
    def set_password(self, user: UserEntity, password: str) -> None:
        ...

    @abstractmethod
    def update_by_data(self, user: UserEntity, data: dict) -> bool:
        ...


class ORMUserRepository(BaseUserRepository):
    def authenticate(self, login: str, password: str) -> UserEntity | None:
        user_dto = authenticate(username=login, password=password)
        return user_to_entity(user_dto) if user_dto else None

    def get_by_email(self, email: str) -> UserEntity | None:
        user_dto = CustomUser.objects.filter(email=email).first()
        return user_to_entity(user_dto) if user_dto else None

    def get_by_id(self, user_id: int) -> UserEntity | None:
        user_dto = CustomUser.objects.filter(pk=user_id).first()
        return user_to_entity(user_dto) if user_dto else None

    def create_by_data(self, data: dict) -> CustomUser:
        return CustomUser.objects.create_user(**data)

    def set_password(self, user: UserEntity, password: str) -> None:
        user_dto = user_from_entity(user=user)
        user_dto.set_password(password)
        user_dto.save()

    def update_by_data(self, user: UserEntity, data: dict) -> bool:
        updated = CustomUser.objects.filter(pk=user.id).update(**data)
        return bool(updated)
