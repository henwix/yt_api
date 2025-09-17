from abc import (
    ABC,
    abstractmethod,
)

from core.project.celery import app


class BaseSenderProvider(ABC):
    @abstractmethod
    def send_code(self, email: str, code: int):
        ...


class EmailSenderProvider(BaseSenderProvider):
    def send_code(self, email: str, code: int):
        app.send_task(
            'core.apps.users.tasks.send_otp_code_email',
            args=[email, code],
            queue='email-queue',
            ignore_result=True,
        )
