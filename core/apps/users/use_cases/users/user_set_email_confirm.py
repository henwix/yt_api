from dataclasses import dataclass

from core.apps.users.entities import UserEntity
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass()
class UserSetEmailConfirmUseCase:
    code_service: BaseCodeService
    user_service: BaseUserService

    def execute(self, user: UserEntity, code: str) -> dict:
        # validate the provided code and update the email for the user
        cached_new_email = self.code_service.validate_set_email_code(user_id=user.id, code=code)
        self.user_service.update_by_data(user=user, data={'email': cached_new_email})

        return {'detail': 'Success', 'new_email': cached_new_email}
