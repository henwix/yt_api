from dataclasses import dataclass

from core.apps.users.entities import UserEntity
from core.apps.users.services.users import BaseUserService


@dataclass
class UserSetPasswordUseCase:
    user_service: BaseUserService

    def execute(self, user: UserEntity, password: str) -> None:
        self.user_service.set_password(user=user, password=password)
