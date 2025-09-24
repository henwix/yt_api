from dataclasses import dataclass

from django.db.utils import settings

from core.apps.common.services.encoding import BaseEncodingService
from core.apps.common.services.smtp_email import BaseEmailService
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass
class UserResetPasswordUseCase:
    user_service: BaseUserService
    code_service: BaseCodeService
    encoding_service: BaseEncodingService
    email_service: BaseEmailService

    def execute(self, email: str) -> dict:
        user = self.user_service.get_by_email_or_404(email=email)

        token = self.code_service.generate_password_reset_code(user=user)
        encoded_id = self.encoding_service.base64_encode(data=user.id)

        self.email_service.send_email(
            to=[user.email],
            context={'username': user.username, 'encoded_id': encoded_id, 'token': token},
            subject='Confirm your password reset',
            template=settings.EMAIL_SMTP_TEMPLATES.get('password_reset'),
        )

        return {'detail': 'Email successfully sent'}
