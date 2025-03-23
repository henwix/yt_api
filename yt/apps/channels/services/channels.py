import logging
from abc import ABC, abstractmethod
from typing import Iterable

from django.core.cache import cache
from rest_framework import status

from ..models import SubscriptionItem
from ..repositories.channels import BaseChannelAvatarRepository, BaseChannelRepository, BaseChannelSubsRepository
from ..serializers import ChannelSerializer

log = logging.getLogger(__name__)


class BaseChannelService(ABC):
    def __init__(self, repository: BaseChannelRepository, serializer_class=ChannelSerializer):
        self.repository = repository
        self.serializer_class = serializer_class

    @abstractmethod
    def get_channel(self, user) -> dict:
        pass

    @abstractmethod
    def delete_channel(self, user):
        pass


class ChannelService(BaseChannelService):
    def get_channel(self, user) -> dict:
        cache_key = f'retrieve_channel_{user.pk}'
        cached_channel = cache.get(cache_key)

        if cached_channel:
            return cached_channel

        channel = self.repository.get_channel(user)
        serializer = self.serializer_class(channel)
        cache.set(key=cache_key, value=serializer.data, timeout=60 * 15)

        return serializer.data

    def delete_channel(self, user):
        self.repository.delete_channel(user)


class BaseChannelSubsService(ABC):
    def __init__(self, repository: BaseChannelSubsRepository):
        self.repository = repository

    @abstractmethod
    def get_subscriber_list(self, channel) -> Iterable[SubscriptionItem]:
        pass


class ChannelSubsService(BaseChannelSubsService):
    def get_subscriber_list(self, channel) -> Iterable[SubscriptionItem]:
        return self.repository.get_subscriber_list(channel=channel)


class ChannelAvatarService:
    def __init__(self, repository: BaseChannelAvatarRepository):
        self.repository = repository

    def delete_avatar(self, channel) -> tuple:
        log.info(hasattr(channel, 'channel_avatar'))
        if not bool(channel.channel_avatar.exists()):
            return {'error': 'Avatar does not exists'}, status.HTTP_404_NOT_FOUND

        try:
            self.repository.delete_avatar(channel)
        except Exception as e:
            log.info('Channel avatar deletion error: %s', e)
            return {'error': 'Something went wrong'}, status.HTTP_400_BAD_REQUEST

        return {'status': 'Success'}, status.HTTP_204_NO_CONTENT
