import logging
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)


class BaseChannelAvatarProvider(ABC):
    @abstractmethod
    def delete_avatar(self, user_pk: int) -> None: ...


class ChannelProvider(BaseChannelAvatarProvider):
    def delete_avatar(self, user_pk: int) -> None:
        #  TODO: пофиксить циклический импорт или сделать это через DI
        from ..tasks import delete_channel_avatar

        task_result = delete_channel_avatar.apply_async(args=[user_pk], ignore_result=True)
        log.info(task_result.id)
