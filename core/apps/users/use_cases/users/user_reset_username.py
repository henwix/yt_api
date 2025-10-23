from dataclasses import dataclass

from django.db.utils import settings

from core.apps.common.constants import (
    CACHE_KEYS,
    EMAIL_SMTP_TEMPLATES,
)
from core.apps.common.services.encoding import BaseEncodingService
from core.apps.common.services.smtp_email import BaseEmailService
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass
class UserResetUsernameUseCase:
    user_service: BaseUserService
    code_service: BaseCodeService
    encoding_service: BaseEncodingService
    email_service: BaseEmailService

    def execute(self, email: str) -> dict:
        # retrieve user by email or raise 404 error
        user = self.user_service.get_by_email_or_404(email=email)

        # generate username reset code and encoded user id
        code = self.code_service.generate_user_email_code(
            user=user,
            cache_prefix=CACHE_KEYS.get('username_reset'),
        )
        encoded_id = self.encoding_service.base64_encode(data=user.id)

        # send email with username reset code
        self.email_service.send_email(
            to=[user.email],
            context={
                'email': user.email,
                'code': code,
                'encoded_id': encoded_id,
                'url': self.email_service.build_email_frontend_url(
                    uri=settings.EMAIL_FRONTEND_USERNAME_RESET_URI,
                    query_params={'uid': encoded_id, 'code': code},
                ),
            },
            subject='Confirm your username reset',
            template=EMAIL_SMTP_TEMPLATES.get('username_reset'),
        )

        return {'detail': 'Confirmation email successfully sent'}
