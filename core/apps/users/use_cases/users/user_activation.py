from dataclasses import dataclass

from django.db.utils import settings

from core.apps.common.services.encoding import BaseEncodingService
from core.apps.users.exceptions.users import InvalidUIDValueError
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import (
    BaseUserActivatedValidatorService,
    BaseUserActivationRequiredValidatorService,
    BaseUserService,
)


@dataclass
class UserActivationUseCase:
    user_service: BaseUserService
    user_validator_service: BaseUserActivatedValidatorService
    activation_validator_service: BaseUserActivationRequiredValidatorService
    code_service: BaseCodeService
    encoding_service: BaseEncodingService

    def execute(self, encoded_id: str, code: str) -> dict:
        # check if the activation feature is enabled
        self.activation_validator_service.validate()

        # decode the user id and get the user
        try:
            decoded_id = self.encoding_service.base64_decode(data=encoded_id)
            user = self.user_service.get_by_id_or_404(user_id=int(decoded_id))

        except (ValueError, TypeError) as error:
            raise InvalidUIDValueError(error_msg=str(error))

        # validate that the user is not already activated
        self.user_validator_service.validate(user=user)

        # validate the code and activate the user by updating the is_active field to True
        self.code_service.validate_user_email_code(
            user=user,
            code=code,
            cache_prefix=settings.CACHE_KEYS.get('activate_user'),
        )
        self.user_service.update_by_data(user=user, data={'is_active': True})

        return {'detail': 'Success'}
