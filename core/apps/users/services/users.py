from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from rest_framework_simplejwt.tokens import RefreshToken

from core.apps.users.converters.users import user_from_entity
from core.apps.users.entities import UserEntity
from core.apps.users.exceptions.users import UserNotFoundError
from core.apps.users.models import CustomUser
from core.apps.users.repositories.users import BaseUserRepository


class BaseUserValidatorService(ABC):
    @abstractmethod
    def validate(self, user: UserEntity | None) -> None:
        ...


class UserExistsValidatorService(BaseUserValidatorService):
    def validate(self, user: UserEntity | None) -> None:
        if not user or user is None:
            raise UserNotFoundError()


@dataclass
class BaseUserService(ABC):
    repository: BaseUserRepository
    validator_service: BaseUserValidatorService

    @abstractmethod
    def authenticate(self, login: str, password: str) -> UserEntity:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity:
        ...

    @abstractmethod
    def generate_jwt(self, user: UserEntity) -> dict:
        ...

    @abstractmethod
    def create_by_data(self, data: dict) -> CustomUser:
        ...

    @abstractmethod
    def set_password(self, user: UserEntity, password: str) -> None:
        ...


class ORMUserService(BaseUserService):
    def authenticate(self, login: str, password: str) -> UserEntity:
        user = self.repository.authenticate(login=login, password=password)
        self.validator_service.validate(user=user)
        return user

    def get_by_email(self, email: str) -> UserEntity:
        user = self.repository.get_by_email(email=email)
        self.validator_service.validate(user=user)
        return user

    def generate_jwt(self, user: UserEntity) -> dict:
        refresh = RefreshToken.for_user(user_from_entity(user))
        access = refresh.access_token
        return {'access': str(access), 'refresh': str(refresh)}

    def create_by_data(self, data: dict) -> CustomUser:
        return self.repository.create_by_data(data=data)

    def set_password(self, user: UserEntity, password: str) -> None:
        self.repository.set_password(user=user, password=password)
