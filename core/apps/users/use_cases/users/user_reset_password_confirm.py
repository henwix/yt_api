from dataclasses import dataclass

from django.db.utils import settings

from core.apps.common.services.encoding import BaseEncodingService
from core.apps.users.exceptions.users import InvalidUIDValueError
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass
class UserResetPasswordConfirmUseCase:
    user_service: BaseUserService
    code_service: BaseCodeService
    encoding_service: BaseEncodingService

    def execute(self, encoded_id: str, code: str, new_password: str) -> dict:
        # decode the encoded user id and retrieve the user or raise 404 error
        try:
            decoded_id = self.encoding_service.base64_decode(data=encoded_id)
            user = self.user_service.get_by_id_or_404(user_id=int(decoded_id))

        except (ValueError, TypeError) as error:
            raise InvalidUIDValueError(error_msg=str(error))

        # validate the provided code and set the new password for the user
        self.code_service.validate_user_email_code(
            user=user,
            code=code,
            cache_prefix=settings.CACHE_KEYS.get('password_reset'),
        )
        self.user_service.set_password(user=user, password=new_password)

        return {'detail': 'Success'}
