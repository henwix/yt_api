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
        # check if activation is required
        self.activation_validator_service.validate()

        # retrieve user by email or raise 404 error
        user = self.user_service.get_by_email_or_404(email=email)

        # validate that user is not activated
        self.user_validator_service.validate(user=user)

        # generate activation code and encoded user id
        code = self.code_service.generate_user_email_code(
            user=user,
            cache_prefix=settings.CACHE_KEYS.get('activate_user'),
        )
        encoded_id = self.encoding_service.base64_encode(data=user.id)

        # send email with activation code
        self.email_service.send_email(
            to=[user.email],
            context={
                'username': user.username,
                'code': code,
                'encoded_id': encoded_id,
                'url': self.email_service.build_email_frontend_url(
                    uri=settings.EMAIL_FRONTEND_ACTIVATE_URI,
                    query_params={'uid': encoded_id, 'code': code},
                ),
            },
            subject='Activate your account',
            template=settings.EMAIL_SMTP_TEMPLATES.get('activate_user'),
        )

        # return message that the email was sent
        return {'detail': 'Activation email successfully sent'}
