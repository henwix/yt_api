from abc import (
    ABC,
    abstractmethod,
)

from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class BaseUserRepository(ABC):
    @abstractmethod
    def authenticate(self, login: str, password: str) -> User: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...


class UserRepository(BaseUserRepository):
    def authenticate(self, login: str, password: str) -> User:
        return authenticate(username=login, password=password)

    def get_by_email(self, email: str) -> User | None:
        return User.objects.filter(email=email).first()
