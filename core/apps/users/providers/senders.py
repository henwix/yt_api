from abc import ABC


class BaseSenderProvider(ABC):
    def send_code(self): ...
