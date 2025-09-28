from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from django.db.utils import settings

from core.apps.common.providers.senders import BaseSenderProvider


@dataclass
class BaseEmailService(ABC):
    email_sender: BaseSenderProvider

    @abstractmethod
    def send_email(self, to: list[str], context: dict, subject: str, template: str) -> None:
        ...

    @abstractmethod
    def build_frontend_email_url_with_code_and_id(self, uri: str, encoded_id: str, code: str) -> str:
        ...


class EmailService(BaseEmailService):
    def send_email(self, to: list[str], context: dict, subject: str, template: str) -> None:
        self.email_sender.send_email(to=to, context=context, subject=subject, template=template)

    def build_frontend_email_url_with_code_and_id(self, uri: str, encoded_id: str, code: str) -> str:
        protocol = settings.EMAIL_FRONTEND_PROTOCOL
        domain = settings.EMAIL_FRONTEND_DOMAIN

        return f'{protocol}://{domain}{uri}?uid={encoded_id}&code={code}'
