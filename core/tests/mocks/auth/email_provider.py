from dataclasses import dataclass

from core.apps.common.providers.senders import BaseSenderProvider


@dataclass
class DummySenderProvider(BaseSenderProvider):
    def send_code(self, email: str, code: int):
        return True
