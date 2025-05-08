from abc import ABC

from core.apps.users.tasks import send_otp_code_email


class BaseSenderProvider(ABC):
    def send_code(self):
        ...


class EmailSenderProvider(BaseSenderProvider):
    def send_code(self, email: str, code: int):
        send_otp_code_email.apply_async(
            args=[email, code],
            queue='email-queue',
            ignore_result=True,
        )
