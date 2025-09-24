from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.providers.senders import BaseSenderProvider


@dataclass
class BaseEmailService(ABC):
    email_sender: BaseSenderProvider

    @abstractmethod
    def send_email(self, to: list[str], context: dict, subject: str, template: str) -> None:
        ...


class EmailService(BaseEmailService):
    def send_email(self, to: list[str], context: dict, subject: str, template: str) -> None:
        self.email_sender.send_email(to=to, context=context, subject=subject, template=template)
