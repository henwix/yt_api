from dataclasses import dataclass

from django.db.utils import settings

from core.apps.common.services.encoding import BaseEncodingService
from core.apps.users.exceptions.users import InvalidUIDValueException
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass
class UserResetUsernameConfirmUseCase:
    user_service: BaseUserService
    code_service: BaseCodeService
    encoding_service: BaseEncodingService

    def execute(self, encoded_id: str, code: str, new_username: str) -> dict:
        try:
            decoded_id = self.encoding_service.base64_decode(data=encoded_id)
            user = self.user_service.get_by_id_or_404(user_id=int(decoded_id))

        except (ValueError, TypeError) as error:
            raise InvalidUIDValueException(error_msg=str(error))

        self.code_service.validate_reset_code(
            user=user,
            code=code,
            cache_prefix=settings.CACHE_KEYS.get('username_reset'),
        )
        self.user_service.update_by_data(user=user, data={'username': new_username})

        return {'detail': 'Success'}
