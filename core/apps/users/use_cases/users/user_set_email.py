from dataclasses import dataclass

from django.db.utils import settings

from core.apps.common.services.smtp_email import BaseEmailService
from core.apps.users.entities import UserEntity
from core.apps.users.services.codes import BaseCodeService


@dataclass
class UserSetEmailUseCase:
    code_service: BaseCodeService
    email_service: BaseEmailService

    def execute(self, user: UserEntity, email: str) -> dict:
        # generate set email code
        code = self.code_service.generate_set_email_code(user_id=user.id, email=email)

        # send email with set email code
        self.email_service.send_email(
            to=[email],
            context={'email': email, 'username': user.username, 'code': code},
            subject='Confirm Your Email Change',
            template=settings.EMAIL_SMTP_TEMPLATES.get('set_email'),
        )

        # return message that the email was sent
        return {'detail': 'Confirmation email successfully sent'}
