from dataclasses import dataclass

from core.apps.common.constants import CACHE_KEYS
from core.apps.common.services.encoding import BaseEncodingService
from core.apps.users.exceptions.users import InvalidUIDValueError
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass
class UserResetUsernameConfirmUseCase:
    user_service: BaseUserService
    code_service: BaseCodeService
    encoding_service: BaseEncodingService

    def execute(self, encoded_id: str, code: str, new_username: str) -> dict:
        # try to decode the encoded user id and retrieve the user or raise 404 error
        try:
            decoded_id = self.encoding_service.base64_decode(data=encoded_id)
            user = self.user_service.get_by_id_or_404(user_id=int(decoded_id))

        except (ValueError, TypeError) as error:
            raise InvalidUIDValueError(error_msg=str(error))

        # validate the provided code and update the username for the user
        self.code_service.validate_user_email_code(
            user=user,
            code=code,
            cache_prefix=CACHE_KEYS.get('username_reset'),
        )
        self.user_service.update_by_data(user=user, data={'username': new_username})

        return {'detail': 'Success'}
