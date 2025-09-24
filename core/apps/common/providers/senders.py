from abc import (
    ABC,
    abstractmethod,
)

from core.project.celery import app


class BaseSenderProvider(ABC):
    @abstractmethod
    def send_email(self, to: list[str], context: dict, subject: str, template: str) -> None:
        ...


class EmailSenderProvider(BaseSenderProvider):
    def send_email(self, to: list[str], context: dict, subject: str, template: str) -> None:
        app.send_task(
            'core.apps.users.tasks.send_email',
            args=[to, context, subject, template],
            queue='email-queue',
            ignore_result=True,
        )
