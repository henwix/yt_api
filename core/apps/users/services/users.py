from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from django.db.utils import (
    IntegrityError,
    settings,
)

from rest_framework_simplejwt.tokens import RefreshToken

from core.apps.users.converters.users import user_from_entity
from core.apps.users.entities import UserEntity
from core.apps.users.exceptions.users import (
    UserActivationNotAllowedError,
    UserAlreadyActivatedError,
    UserNotFoundError,
    UserWithThisDataAlreadyExistsError,
)
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


class BaseUserActivatedValidatorService(ABC):
    @abstractmethod
    def validate(self, user: UserEntity) -> None:
        ...


class UserActivatedValidatorService(BaseUserActivatedValidatorService):
    def validate(self, user: UserEntity) -> None:
        if user.is_active:
            raise UserAlreadyActivatedError(user_id=user.id)


@dataclass
class BaseUserActivationRequiredValidatorService(ABC):
    user_service: 'BaseUserService'

    @abstractmethod
    def validate(self) -> None:
        ...


class UserActivationRequiredValidatorService(BaseUserActivationRequiredValidatorService):
    def validate(self) -> None:
        if not self.user_service.is_activation_required():
            raise UserActivationNotAllowedError()


@dataclass
class BaseUserService(ABC):
    repository: BaseUserRepository
    validator_service: BaseUserValidatorService

    @abstractmethod
    def authenticate(self, login: str, password: str) -> UserEntity:
        ...

    @abstractmethod
    def get_by_email_or_404(self, email: str) -> UserEntity:
        ...

    @abstractmethod
    def get_by_id_or_404(self, user_id: int) -> UserEntity:
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

    @abstractmethod
    def update_by_data(self, user: UserEntity, data: dict) -> bool:
        ...

    @abstractmethod
    def is_activation_required(self) -> bool:
        ...


class ORMUserService(BaseUserService):
    def authenticate(self, login: str, password: str) -> UserEntity:
        user = self.repository.authenticate(login=login, password=password)
        self.validator_service.validate(user=user)
        return user

    def get_by_email_or_404(self, email: str) -> UserEntity:
        user = self.repository.get_by_email(email=email)
        self.validator_service.validate(user=user)
        return user

    def get_by_id_or_404(self, user_id: int) -> UserEntity:
        user = self.repository.get_by_id(user_id=user_id)
        self.validator_service.validate(user=user)
        return user

    def generate_jwt(self, user: UserEntity) -> dict:
        refresh = RefreshToken.for_user(user_from_entity(user))
        access = refresh.access_token
        return {'access': str(access), 'refresh': str(refresh)}

    def create_by_data(self, data: dict) -> CustomUser:
        try:
            return self.repository.create_by_data(data=data)

        except IntegrityError:
            raise UserWithThisDataAlreadyExistsError()

    def set_password(self, user: UserEntity, password: str) -> None:
        self.repository.set_password(user=user, password=password)

    def update_by_data(self, user: UserEntity, data: dict) -> bool:
        try:
            return self.repository.update_by_data(user=user, data=data)

        except IntegrityError:
            raise UserWithThisDataAlreadyExistsError()

    def is_activation_required(self) -> bool:
        return settings.AUTH_SEND_ACTIVATION_EMAIL
