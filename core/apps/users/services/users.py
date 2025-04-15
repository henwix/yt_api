from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken

from core.apps.users.exceptions.users import UserNotFoundError
from core.apps.users.repositories.users import BaseUserRepository


class BaseUserValidatorService(ABC):
    @abstractmethod
    def validate(self, user: User) -> None: ...


class UserValidatorService(BaseUserValidatorService):
    def validate(self, user: User) -> None:
        if not user:
            raise UserNotFoundError()


@dataclass
class BaseUserService(ABC):
    repository: BaseUserRepository
    validator_service: BaseUserValidatorService

    @abstractmethod
    def authenticate(self, login: str, password: str) -> User: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User: ...

    @abstractmethod
    def generate_jwt(self, user: User) -> dict: ...


class UserService(BaseUserService):
    def authenticate(self, login, password) -> User:
        user = self.repository.authenticate(login=login, password=password)
        self.validator_service.validate(user=user)
        return user

    def get_by_email(self, email: str) -> User:
        user = self.repository.get_by_email(email=email)
        self.validator_service.validate(user=user)
        return user

    def generate_jwt(self, user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        return {'refresh': refresh, 'access': access}
