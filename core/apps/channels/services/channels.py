import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Tuple, Type

from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.serializers import Serializer

from ..exceptions.channels import (
    AvatarDoesNotExistsError,
    AvatarExceptionError,
    ChannelNotFoundError,
    SelfSubscriptionError,
    SubscriptionDoesNotExistsError,
    SubscriptionExistsError,
)
from ..models import Channel, SubscriptionItem
from ..providers.channels import BaseChannelAvatarProvider
from ..repositories.channels import (
    BaseChannelAboutRepository,
    BaseChannelAvatarRepository,
    BaseChannelMainRepository,
    BaseChannelRepository,
    BaseChannelSubsRepository,
    BaseSubscriptionRepository,
)

log = logging.getLogger(__name__)


@dataclass(eq=False)
# FIXME: mb убрать serializer
class BaseChannelService(ABC):
    repository: BaseChannelRepository
    serializer_class: Type[Serializer]

    @abstractmethod
    def get_channel(self, user: User) -> dict:
        pass

    @abstractmethod
    def delete_channel(self, user: User) -> None:
        pass


class CachedORMChannelService(BaseChannelService):
    # TODO:  перенести в отдельный CacheService в common для переиспользования
    def get_channel(self, user: User) -> dict:
        cache_key = f'retrieve_channel_{user.pk}'
        cached_channel = cache.get(cache_key)

        if cached_channel:
            return cached_channel

        channel = self.repository.get_channel_by_user(user)
        if channel is None:
            raise ChannelNotFoundError(user=user)

        serializer = self.serializer_class(channel)
        cache.set(key=cache_key, value=serializer.data, timeout=60 * 15)

        return serializer.data

    def delete_channel(self, user: User) -> None:
        self.repository.delete_channel(user)


@dataclass(eq=False)
class BaseChannelSubsService(ABC):
    repository: BaseChannelSubsRepository

    @abstractmethod
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]:
        pass


class ChannelSubsService(BaseChannelSubsService):
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]:
        return self.repository.get_subscriber_list(channel=channel)


@dataclass(eq=False)
class BaseAvatarValidatorService(ABC):
    @abstractmethod
    def validate_avatar(self, channel: Channel) -> None:
        pass


class AvatarValidatorService(BaseAvatarValidatorService):
    def validate_avatar(self, channel: Channel) -> None:
        if not bool(channel.channel_avatar):
            raise AvatarDoesNotExistsError()


@dataclass(eq=False)
class BaseChannelAvatarService(ABC):
    @abstractmethod
    def delete_avatar(self, user: User) -> dict:
        pass


@dataclass
class ChannelAvatarService(BaseChannelAvatarService):
    avatar_repository: BaseChannelAvatarRepository
    channel_repository: BaseChannelRepository
    validator_service: BaseAvatarValidatorService

    def delete_avatar(self, user: User) -> dict:
        channel = self.channel_repository.get_channel_by_user(user)

        self.validator_service.validate_avatar(channel)

        try:
            self.avatar_repository.delete_avatar(channel)
        except Exception as e:
            log.info('Channel avatar deletion error: %s', e)
            raise AvatarExceptionError(channel=channel)
        else:
            return {'status': 'Success'}


@dataclass
class CeleryChannelAvatarService(BaseChannelAvatarService):
    provider: BaseChannelAvatarProvider
    channel_repository: BaseChannelRepository
    validator_service: BaseAvatarValidatorService

    def delete_avatar(self, user: User) -> dict:
        channel = self.channel_repository.get_channel_by_id(user.pk)
        self.validator_service.validate_avatar(channel)

        self.provider.delete_avatar(user.pk)
        return {'Status': 'Your avatar will be deleted soon, it can take a few minutes'}


@dataclass(eq=False)
class BaseChannelMainService(ABC):
    repository: BaseChannelMainRepository

    @abstractmethod
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        pass


class ChannelMainService(BaseChannelMainService):
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_main_page_list()


@dataclass(eq=False)
class BaseChannelAboutService(ABC):
    repository: BaseChannelAboutRepository

    @abstractmethod
    def get_channel_about_list(self) -> Iterable[Channel]:
        pass


class ChannelAboutService(BaseChannelAboutService):
    def get_channel_about_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_about_list()


@dataclass(eq=False)
class BaseSubscriptionService(ABC):
    repository: BaseSubscriptionRepository

    @abstractmethod
    def subscribe(self, user: User, slug: str) -> dict:
        pass

    @abstractmethod
    def unsubscribe(self, user: User, slug: str) -> dict:
        pass


class SubscriptionService(BaseSubscriptionService):
    def _validate_subscription(self, user: User, slug: str) -> Tuple[Channel, Channel]:
        subscriber, subscribed_to = self.repository.get_channels(user, slug)

        if not subscribed_to:
            raise ChannelNotFoundError()

        if not subscriber.pk != subscribed_to.pk:
            raise SelfSubscriptionError()

        return subscriber, subscribed_to

    def subscribe(self, user: User, slug: str) -> dict:
        subscriber, subscribed_to = self._validate_subscription(user, slug)

        _, created = self.repository.get_or_create_sub(subscriber=subscriber, subscribed_to=subscribed_to)

        if not created:
            raise SubscriptionExistsError()

        return {'status': 'Subscription created'}

    def unsubscribe(self, user: User, slug: str) -> dict:
        subscriber, subscribed_to = self._validate_subscription(user, slug)

        deleted, _ = self.repository.delete_sub(subscriber=subscriber, subscribed_to=subscribed_to)

        if not deleted:
            raise SubscriptionDoesNotExistsError()

        return {'status': 'Subscription deleted'}
