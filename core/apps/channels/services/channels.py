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
from django.contrib.auth.models import AnonymousUser

from core.apps.channels.exceptions.subscriptions import (
    SelfSubscriptionError,
    SubscriptionDoesNotExistsError,
    SubscriptionExistsError,
)

from ..exceptions.channels import (
    ChannelNotFoundError,
    SlugChannelNotFoundError,
)
from ..models import (
    Channel,
    SubscriptionItem,
)
from ..repositories.channels import (
    BaseChannelAboutRepository,
    BaseChannelMainRepository,
    BaseChannelRepository,
    BaseChannelSubsRepository,
    BaseSubscriptionRepository,
)


User = get_user_model()


@dataclass(eq=False)
class BaseChannelService(ABC):
    repository: BaseChannelRepository

    @abstractmethod
    def get_channel_by_user_or_404(self, user: User) -> Channel:
        ...

    @abstractmethod
    def get_channel_by_user_or_none(self, user: User) -> Channel | None:
        ...

    @abstractmethod
    def delete_channel(self, user: User) -> None:
        ...

    @abstractmethod
    def set_avatar_s3_key(self, channel: Channel, avatar_s3_key: str | None) -> None:
        ...


class ORMChannelService(BaseChannelService):
    def get_channel_by_user_or_404(self, user: User) -> Channel:
        channel = self.repository.get_channel_by_user(user)
        if channel is None:
            raise ChannelNotFoundError(user_id=user.pk)

        return channel

    def get_channel_by_user_or_none(self, user: User) -> Channel | None:
        if isinstance(user, AnonymousUser):
            return None
        return self.repository.get_channel_by_user(user)

    def delete_channel(self, user: User) -> None:
        self.repository.delete_channel(user)

    def set_avatar_s3_key(self, channel: Channel, avatar_s3_key: str | None) -> None:
        self.repository.set_avatar_s3_key(channel=channel, avatar_s3_key=avatar_s3_key)


@dataclass(eq=False)
class BaseChannelSubsService(ABC):
    repository: BaseChannelSubsRepository

    @abstractmethod
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]: ...


class ORMChannelSubsService(BaseChannelSubsService):
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]:
        return self.repository.get_subscriber_list(channel=channel).select_related('subscriber', 'subscribed_to')


@dataclass(eq=False)
class BaseChannelMainService(ABC):
    repository: BaseChannelMainRepository

    @abstractmethod
    def get_channel_main_page_list(self) -> Iterable[Channel]: ...


class ORMChannelMainService(BaseChannelMainService):
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_main_page_list()


@dataclass(eq=False)
class BaseChannelAboutService(ABC):
    repository: BaseChannelAboutRepository

    @abstractmethod
    def get_channel_about_list(self) -> Iterable[Channel]: ...


class ORMChannelAboutService(BaseChannelAboutService):
    def get_channel_about_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_about_list()


@dataclass(eq=False)
class BaseSubscriptionService(ABC):
    repository: BaseSubscriptionRepository

    @abstractmethod
    def subscribe(self, user: User, channel_slug: str) -> dict: ...

    @abstractmethod
    def unsubscribe(self, user: User, channel_slug: str) -> dict: ...


class ORMSubscriptionService(BaseSubscriptionService):
    def validate_subscription(self, user: User, channel_slug: str) -> Tuple[Channel, Channel]:
        subscriber, subscribed_to = self.repository.get_channels(user, channel_slug)

        if not subscribed_to:
            raise SlugChannelNotFoundError(channel_slug=user.pk)

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
