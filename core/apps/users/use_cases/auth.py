from dataclasses import dataclass
from logging import Logger

from django.db.utils import settings

from core.apps.common.services.smtp_email import BaseEmailService
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


# TODO: закинуть в одельные файлы + сделать папки для `oauth2` и `auth`
@dataclass
class AuthorizeUserUseCase:
    user_service: BaseUserService
    code_service: BaseCodeService
    email_service: BaseEmailService

    def execute(self, login: str, password: str) -> dict:
        user = self.user_service.authenticate(login=login, password=password)

        if not user.otp_enabled:
            tokens = self.user_service.generate_jwt(user=user)
            return tokens

        code = self.code_service.generate_email_otp_code(email=user.email)
        self.email_service.send_email(
            to=[user.email],
            context={'email': user.email, 'code': code},
            subject='OTP Email Confirmation',
            template=settings.EMAIL_SMTP_TEMPLATES.get('otp_email'),
        )

        return {'detail': 'Email successfully sent'}


@dataclass
class VerifyCodeUseCase:
    code_service: BaseCodeService
    user_service: BaseUserService
    logger: Logger

    def execute(self, email: str, code: str) -> dict:
        self.code_service.validate_email_otp_code(email=email, code=code)

        user = self.user_service.get_by_email_or_404(email=email)
        tokens = self.user_service.generate_jwt(user=user)

        return tokens
