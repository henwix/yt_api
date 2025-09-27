from dataclasses import dataclass

from django.db.utils import settings

from core.apps.common.services.encoding import BaseEncodingService
from core.apps.common.services.smtp_email import BaseEmailService
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import (
    BaseUserActivatedValidatorService,
    BaseUserActivationRequiredValidatorService,
    BaseUserService,
)


@dataclass
class UserResendActivationUseCase:
    user_service: BaseUserService
    email_service: BaseEmailService
    code_service: BaseCodeService
    encoding_service: BaseEncodingService
    activation_validator_service: BaseUserActivationRequiredValidatorService
    user_validator_service: BaseUserActivatedValidatorService

    def execute(self, email: str) -> dict:
        self.activation_validator_service.validate()

        user = self.user_service.get_by_email_or_404(email=email)

        self.user_validator_service.validate(user=user)

        code = self.code_service.generate_user_email_code(
            user=user,
            cache_prefix=settings.CACHE_KEYS.get('activate_user'),
        )
        encoded_id = self.encoding_service.base64_encode(data=user.id)

        self.email_service.send_email(
            to=[user.email],
            context={'username': user.username, 'encoded_id': encoded_id, 'code': code},
            subject='Activate your account',
            template=settings.EMAIL_SMTP_TEMPLATES.get('activate_user'),
        )

        return {'detail': 'Activation email successfully sent'}
