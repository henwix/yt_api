from dataclasses import dataclass

from django.db.utils import settings

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
        user = self.user_service.get_by_email_or_404(email=email)

        code = self.code_service.generate_user_email_code(
            user=user,
            cache_prefix=settings.CACHE_KEYS.get('username_reset'),
        )
        encoded_id = self.encoding_service.base64_encode(data=user.id)

        # TODO: при отправке письма для резета юзернейма или пароля добавлять не тупо токен + uid
        # а строить целую ссылку на фронт. В env добавить protocol, domain, uri для фронта и
        # сделать метод внутри email_service, чтобы автоматом строить эту ссылку
        self.email_service.send_email(
            to=[user.email],
            context={'email': user.email, 'encoded_id': encoded_id, 'code': code},
            subject='Confirm your username reset',
            template=settings.EMAIL_SMTP_TEMPLATES.get('username_reset'),
        )

        return {'detail': 'Email successfully sent'}
