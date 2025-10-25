from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from urllib.parse import urlencode

from django.db.utils import settings

from core.apps.common.providers.senders import BaseSenderProvider


@dataclass
class BaseEmailService(ABC):
    email_sender: BaseSenderProvider

    @abstractmethod
    def send_email(self, to: list[str], context: dict, subject: str, template: str) -> None: ...

    @abstractmethod
    def build_email_frontend_url(self, uri: str, query_params: dict | None = None) -> str: ...


class EmailService(BaseEmailService):
    def send_email(self, to: list[str], context: dict, subject: str, template: str) -> None:
        self.email_sender.send_email(to=to, context=context, subject=subject, template=template)

    def build_email_frontend_url(self, uri: str, query_params: dict | None = None) -> str:
        base_url = f'{settings.EMAIL_FRONTEND_PROTOCOL}://{settings.EMAIL_FRONTEND_DOMAIN}{uri}'

        if query_params:
            return base_url + '?' + urlencode(query_params)
        return base_url
