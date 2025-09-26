from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from django.utils.encoding import (
    force_bytes,
    force_str,
)
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)


@dataclass
class BaseEncodingService(ABC):
    @abstractmethod
    def base64_encode(self, data: str | int) -> str:
        ...

    @abstractmethod
    def base64_decode(self, data: bytes) -> str:
        ...


class EncodingService(BaseEncodingService):
    def base64_encode(self, data: str | int) -> str:
        return urlsafe_base64_encode(force_bytes(data))

    def base64_decode(self, data: bytes) -> str:
        """Encodes data from base64 to string.

        ***Be sure that you handle possible encoding exceptions outside
        of this method***

        """

        return force_str(urlsafe_base64_decode(data))
