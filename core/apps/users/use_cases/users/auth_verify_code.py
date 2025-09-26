from dataclasses import dataclass
from logging import Logger

from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


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
