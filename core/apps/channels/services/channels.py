import logging
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Iterable,
    Tuple,
)

from django.contrib.auth import get_user_model

from core.apps.channels.exceptions.subscriptions import (
    SelfSubscriptionError,
    SubscriptionDoesNotExistsError,
    SubscriptionExistsError,
)

from ..exceptions.channels import (
    AvatarDoesNotExistsError,
    AvatarExceptionError,
    ChannelNotFoundError,
)
from ..models import (
    Channel,
    SubscriptionItem,
)
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
User = get_user_model()


@dataclass(eq=False)
class BaseChannelService(ABC):
    repository: BaseChannelRepository

    @abstractmethod
    def get_channel(self, user: User) -> Channel: ...

    @abstractmethod
    def delete_channel(self, user: User) -> None: ...


class ORMChannelService(BaseChannelService):
    def get_channel(self, user: User) -> Channel:
        channel = self.repository.get_channel_by_user(user)
        if channel is None:
            raise ChannelNotFoundError(user_id=user.pk)

        return channel

    def delete_channel(self, user: User) -> None:
        self.repository.delete_channel(user)


@dataclass(eq=False)
class BaseChannelSubsService(ABC):
    repository: BaseChannelSubsRepository

    @abstractmethod
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]: ...


class ChannelSubsService(BaseChannelSubsService):
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]:
        return self.repository.get_subscriber_list(channel=channel).select_related('subscriber', 'subscribed_to')


@dataclass(eq=False)
class BaseAvatarValidatorService(ABC):
    @abstractmethod
    def validate_avatar(self, channel: Channel) -> None: ...


class AvatarValidatorService(BaseAvatarValidatorService):
    def validate_avatar(self, channel: Channel) -> None:
        if not bool(channel.channel_avatar):
            raise AvatarDoesNotExistsError(channel_slug=channel.slug)


@dataclass(eq=False)
class BaseChannelAvatarService(ABC):
    @abstractmethod
    def delete_avatar(self, user: User) -> dict: ...


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
            raise AvatarExceptionError(channel_slug=channel.slug)
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
        return {'status': 'Your avatar will be deleted soon, it can take a few minutes'}


@dataclass(eq=False)
class BaseChannelMainService(ABC):
    repository: BaseChannelMainRepository

    @abstractmethod
    def get_channel_main_page_list(self) -> Iterable[Channel]: ...


class ChannelMainService(BaseChannelMainService):
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_main_page_list()


@dataclass(eq=False)
class BaseChannelAboutService(ABC):
    repository: BaseChannelAboutRepository

    @abstractmethod
    def get_channel_about_list(self) -> Iterable[Channel]: ...


class ChannelAboutService(BaseChannelAboutService):
    def get_channel_about_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_about_list()


@dataclass(eq=False)
class BaseSubscriptionService(ABC):
    repository: BaseSubscriptionRepository

    @abstractmethod
    def subscribe(self, user: User, channel_slug: str) -> dict: ...

    @abstractmethod
    def unsubscribe(self, user: User, channel_slug: str) -> dict: ...


class SubscriptionService(BaseSubscriptionService):
    def validate_subscription(self, user: User, channel_slug: str) -> Tuple[Channel, Channel]:
        subscriber, subscribed_to = self.repository.get_channels(user, channel_slug)

        if not subscribed_to:
            raise ChannelNotFoundError(user_id=user.pk)

        if subscriber.pk == subscribed_to.pk:
            raise SelfSubscriptionError(channel_slug=subscriber.slug)

        return subscriber, subscribed_to

    def subscribe(self, user: User, channel_slug: str) -> dict:
        subscriber, subscribed_to = self.validate_subscription(user, channel_slug)

        _, created = self.repository.get_or_create_sub(subscriber=subscriber, subscribed_to=subscribed_to)

        if not created:
            raise SubscriptionExistsError(sub_slug=subscriber.slug, sub_to_slug=subscribed_to.slug)

        return {'status': 'Subscription created'}

    def unsubscribe(self, user: User, channel_slug: str) -> dict:
        subscriber, subscribed_to = self.validate_subscription(user, channel_slug)

        deleted, _ = self.repository.delete_sub(subscriber=subscriber, subscribed_to=subscribed_to)

        if not deleted:
            raise SubscriptionDoesNotExistsError(sub_slug=subscriber.slug, sub_to_slug=subscribed_to.slug)

        return {'status': 'Subscription deleted'}
