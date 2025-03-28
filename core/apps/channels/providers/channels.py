from abc import ABC, abstractmethod


class BaseChannelAvatarProvider(ABC):
    @abstractmethod
    def delete_avatar(self, user_pk: int) -> None:
        pass


class ChannelProvider(BaseChannelAvatarProvider):
    def delete_avatar(self, user_pk: int) -> None:
        #  TODO: пофиксить циклический импорт или сделать это через DI
        from ..tasks import delete_channel_avatar
        delete_channel_avatar.apply_async(args=[user_pk], ignore_result=True)
