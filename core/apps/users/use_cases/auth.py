from dataclasses import dataclass

from core.apps.users.providers.senders import BaseSenderProvider
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass
class AuthorizeUserUseCase:
    user_service: BaseUserService
    code_service: BaseCodeService
    sender_provider: BaseSenderProvider

    def execute(self, login: str, password: str) -> dict:
        user = self.user_service.authenticate(login=login, password=password)

        if not user.otp_enabled:
            tokens = self.user_service.generate_jwt(user=user)
            return tokens

        code = self.code_service.generate_code(email=user.email)
        self.sender_provider.send_code(email=user.email, code=code)

        return {'status': 'email successfully sent'}


@dataclass
class VerifyCodeUseCase:
    code_service: BaseCodeService
    user_service: BaseUserService

    def execute(self, email: str, code: str) -> dict:
        self.code_service.validate_code(email=email, code=code)

        user = self.user_service.get_by_email(email=email)
        tokens = self.user_service.generate_jwt(user=user)

        return tokens
