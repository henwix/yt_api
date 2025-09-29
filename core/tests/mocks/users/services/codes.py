import uuid
from dataclasses import dataclass

from core.apps.users.services.codes import EmailCodeService


@dataclass
class DummyEmailCodeService(EmailCodeService):
    def generate_set_email_code(self, user_id: int, email: str) -> str:
        return uuid.uuid4().hex
