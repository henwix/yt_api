import logging
from abc import (
    ABC,
    abstractmethod,
)


log = logging.getLogger(__name__)


class BaseChannelAvatarProvider(ABC):
    @abstractmethod
    def delete_avatar(self, user_pk: int) -> None:
        ...


class CeleryChannelProvider(BaseChannelAvatarProvider):
    def delete_avatar(self, user_pk: int) -> None:
        from ..tasks import delete_channel_avatar

        delete_channel_avatar.apply_async(args=[user_pk], queue='media-queue', ignore_result=True)
