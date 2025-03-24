import logging
from abc import ABC, abstractmethod
from ast import Tuple
from typing import Iterable, Type

from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework import status
from rest_framework.serializers import Serializer

from ..models import Channel, SubscriptionItem
from ..repositories.channels import (
    BaseChannelAboutRepository,
    BaseChannelAvatarRepository,
    BaseChannelMainRepository,
    BaseChannelRepository,
    BaseChannelSubsRepository,
    BaseSubscriptionRepository,
)

log = logging.getLogger(__name__)


class BaseChannelService(ABC):
    def __init__(self, repository: BaseChannelRepository, serializer_class: Type[Serializer]):
        self.repository = repository
        self.serializer_class = serializer_class

    @abstractmethod
    def get_channel(self, user: User) -> dict:
        pass

    @abstractmethod
    def delete_channel(self, user: User) -> None:
        pass


class CachedORMChannelService(BaseChannelService):
    def get_channel(self, user: User) -> dict:
        cache_key = f'retrieve_channel_{user.pk}'
        cached_channel = cache.get(cache_key)

        if cached_channel:
            return cached_channel

        channel = self.repository.get_channel(user)
        serializer = self.serializer_class(channel)
        cache.set(key=cache_key, value=serializer.data, timeout=60 * 15)

        return serializer.data

    def delete_channel(self, user: User) -> None:
        self.repository.delete_channel(user)


class BaseChannelSubsService(ABC):
    def __init__(self, repository: BaseChannelSubsRepository):
        self.repository = repository

    @abstractmethod
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]:
        pass


class ChannelSubsService(BaseChannelSubsService):
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]:
        return self.repository.get_subscriber_list(channel=channel)


class BaseChannelAvatarService(ABC):
    def __init__(self, repository: BaseChannelAvatarRepository):
        self.repository = repository

    @abstractmethod
    def delete_avatar(self, channel: Channel) -> Tuple[dict, int]:
        pass


class ChannelAvatarService(BaseChannelAvatarService):
    def delete_avatar(self, channel: Channel) -> Tuple[dict, int]:
        if not bool(channel.channel_avatar):
            return {'error': 'Avatar does not exists'}, status.HTTP_404_NOT_FOUND

        try:
            self.repository.delete_avatar(channel)
        except Exception as e:
            log.info('Channel avatar deletion error: %s', e)
            return {'error': 'Something went wrong'}, status.HTTP_400_BAD_REQUEST

        return {'status': 'Success'}, status.HTTP_204_NO_CONTENT


class BaseChannelMainService(ABC):
    def __init__(self, repository: BaseChannelMainRepository):
        self.repository = repository

    @abstractmethod
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        pass


class ChannelMainService(BaseChannelMainService):
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_main_page_list()


class BaseChannelAboutService(ABC):
    def __init__(self, repository: BaseChannelAboutRepository):
        self.repository = repository

    @abstractmethod
    def get_channel_about_list(self) -> Iterable[Channel]:
        pass


class ChannelAboutService(BaseChannelAboutService):
    def get_channel_about_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_about_list()


class BaseSubscriptionService(ABC):
    def __init__(self, repository: BaseSubscriptionRepository):
        self.repository = repository

    @abstractmethod
    def subscribe(self, user: User, slug: str) -> Tuple[dict, int]:
        pass

    @abstractmethod
    def unsubscribe(self, user: User, slug: str) -> Tuple[dict, int]:
        pass


class SubscriptionService(BaseSubscriptionService):
    def _validate_subscription(
        self, user: User, slug: str
    ) -> Tuple[Channel | None, Channel | None, dict | None, int | None]:
        subscriber, subscribed_to = self.repository.get_channels(user, slug)

        if not subscribed_to:
            return (
                None,
                None,
                {'error': 'The channel you want to subscribe does not exists'},
                status.HTTP_404_NOT_FOUND,
            )

        if not subscriber.pk != subscribed_to.pk:
            return (None, None, {'error': 'You cannot subscribe to yourself'}, status.HTTP_400_BAD_REQUEST)
        return subscriber, subscribed_to, None, None

    def subscribe(self, user: User, slug: str) -> Tuple[dict, int]:
        subscriber, subscribed_to, error, error_status = self._validate_subscription(user, slug)

        if error:
            return error, error_status

        _, created = self.repository.get_or_create_sub(subscriber=subscriber, subscribed_to=subscribed_to)

        if created:
            return {'status': 'Success: Sub created'}, status.HTTP_201_CREATED

        return {'status': 'Already subscribed'}, status.HTTP_200_OK

    def unsubscribe(self, user: User, slug: str) -> Tuple[dict, int]:
        subscriber, subscribed_to, error, error_status = self._validate_subscription(user, slug)

        if error:
            return error, error_status

        deleted, _ = self.repository.delete_sub(subscriber=subscriber, subscribed_to=subscribed_to)

        if deleted:
            return {'status': 'Success: Sub deleted'}, status.HTTP_204_NO_CONTENT

        return {'error': 'Subscription does not exists'}, status.HTTP_404_NOT_FOUND
