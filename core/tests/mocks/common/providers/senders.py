from dataclasses import dataclass

from core.apps.common.providers.senders import BaseSenderProvider


@dataclass
class DummySenderProvider(BaseSenderProvider):
    def send_email(self, to: list[str], context: dict, subject: str, template: str):
        return True
