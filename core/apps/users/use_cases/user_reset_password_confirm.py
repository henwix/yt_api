from dataclasses import dataclass

from core.apps.common.services.encoding import BaseEncodingService
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass
class UserResetPasswordConfirmUseCase:
    user_service: BaseUserService
    code_service: BaseCodeService
    encoding_service: BaseEncodingService

    def execute(self, encoded_id: str, code: str, new_password: str) -> dict:
        decoded_id = self.encoding_service.base64_decode(data=encoded_id)
        user = self.user_service.get_by_id_or_404(user_id=int(decoded_id))

        self.code_service.validate_password_reset_code(user=user, code=code)
        self.user_service.set_password(user=user, password=new_password)

        return {'detail': 'New password successfully set'}
