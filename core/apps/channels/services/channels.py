import uuid
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from core.apps.channels.converters.channels import data_to_channel_entity
from core.apps.channels.entities.channels import ChannelEntity
from core.apps.channels.exceptions.channels import (
    ChannelNotFoundError,
    SlugChannelNotFoundError,
)
from core.apps.channels.exceptions.subscriptions import (
    SelfSubscriptionError,
    SubscriptionDoesNotExistsError,
    SubscriptionExistsError,
)
from core.apps.channels.models import (
    Channel,
    SubscriptionItem,
)
from core.apps.channels.repositories.channels import (
    BaseChannelAboutRepository,
    BaseChannelMainRepository,
    BaseChannelRepository,
    BaseChannelSubsRepository,
    BaseSubscriptionRepository,
)
from core.apps.users.entities import (
    AnonymousUserEntity,
    UserEntity,
)


@dataclass(eq=False)
class BaseChannelService(ABC):
    repository: BaseChannelRepository

    @abstractmethod
    def create_channel_by_user_info(self, user: UserEntity) -> ChannelEntity:
        ...

    @abstractmethod
    def get_channel_by_user_or_404(self, user: UserEntity | AnonymousUserEntity) -> ChannelEntity:
        ...

    @abstractmethod
    def get_channel_by_user_or_none(self, user: UserEntity) -> ChannelEntity | None:
        ...

    @abstractmethod
    def delete_channel(self, user: UserEntity) -> None:
        ...

    @abstractmethod
    def set_avatar_s3_key(self, channel: ChannelEntity, avatar_s3_key: str | None) -> None:
        ...


class ORMChannelService(BaseChannelService):
    def create_channel_by_user_info(self, user: UserEntity) -> ChannelEntity:
        channel_data = {}

        channel_data['name'] = user.username
        channel_data['user_id'] = user.id

        slug = user.username
        if self.repository.is_slug_exists(slug):
            slug += '_' + uuid.uuid4()[:8]

        channel_data['slug'] = slug

        return self.repository.channel_create(channel_entity=data_to_channel_entity(channel_data))

    def get_channel_by_user_or_404(self, user: UserEntity | AnonymousUserEntity) -> ChannelEntity:
        if user.is_anonymous:
            raise ChannelNotFoundError('Anonymous')

        channel = self.repository.get_channel_by_user_or_none(user)

        if channel is None:
            raise ChannelNotFoundError(user_id=user.id)
        return channel

    def get_channel_by_user_or_none(self, user: UserEntity | AnonymousUserEntity) -> ChannelEntity | None:
        if user.is_anonymous:
            return None
        return self.repository.get_channel_by_user_or_none(user)

    def delete_channel(self, user: UserEntity) -> None:
        self.repository.delete_channel_by_user(user)

    def set_avatar_s3_key(self, channel: ChannelEntity, avatar_s3_key: str | None) -> None:
        self.repository.set_avatar_s3_key(channel=channel, avatar_s3_key=avatar_s3_key)


@dataclass(eq=False)
class BaseChannelSubsService(ABC):
    repository: BaseChannelSubsRepository

    @abstractmethod
    def get_subscriber_list(self, channel: ChannelEntity) -> Iterable[SubscriptionItem]:
        ...


class ORMChannelSubsService(BaseChannelSubsService):
    def get_subscriber_list(self, channel: ChannelEntity) -> Iterable[SubscriptionItem]:
        return self.repository.get_subscriber_list(channel=channel).select_related('subscriber', 'subscribed_to')


@dataclass(eq=False)
class BaseChannelMainService(ABC):
    repository: BaseChannelMainRepository

    @abstractmethod
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        ...


class ORMChannelMainService(BaseChannelMainService):
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_main_page_list()


@dataclass(eq=False)
class BaseChannelAboutService(ABC):
    repository: BaseChannelAboutRepository

    @abstractmethod
    def get_channel_about_list(self) -> Iterable[Channel]:
        ...


class ORMChannelAboutService(BaseChannelAboutService):
    def get_channel_about_list(self) -> Iterable[Channel]:
        return self.repository.get_channel_about_list()


@dataclass(eq=False)
class BaseSubscriptionService(ABC):
    subscription_repository: BaseSubscriptionRepository
    channel_repository: BaseChannelRepository

    @abstractmethod
    def subscribe(self, user: UserEntity, channel_slug: str) -> dict:
        ...

    @abstractmethod
    def unsubscribe(self, user: UserEntity, channel_slug: str) -> dict:
        ...


class ORMSubscriptionService(BaseSubscriptionService):
    def _validate_subscription(self, user: UserEntity, channel_slug: str) -> tuple[ChannelEntity, ChannelEntity]:
        subscriber = self.channel_repository.get_channel_by_user_or_none(user)
        subscribed_to = self.channel_repository.get_channel_by_slug(channel_slug)

        if not subscribed_to:
            raise SlugChannelNotFoundError(channel_slug=user.id)

        if subscriber.id == subscribed_to.id:
            raise SelfSubscriptionError(channel_slug=subscriber.slug)

        return subscriber, subscribed_to

    def subscribe(self, user: UserEntity, channel_slug: str) -> dict:
        subscriber, subscribed_to = self._validate_subscription(user, channel_slug)

        _, created = self.subscription_repository.get_or_create_sub(subscriber=subscriber, subscribed_to=subscribed_to)

        if not created:
            raise SubscriptionExistsError(sub_slug=subscriber.slug, sub_to_slug=subscribed_to.slug)

        return {'detail': 'Success'}

    def unsubscribe(self, user: UserEntity, channel_slug: str) -> dict:
        subscriber, subscribed_to = self._validate_subscription(user, channel_slug)

        deleted = self.subscription_repository.delete_sub(subscriber=subscriber, subscribed_to=subscribed_to)

        if not deleted:
            raise SubscriptionDoesNotExistsError(sub_slug=subscriber.slug, sub_to_slug=subscribed_to.slug)

        return {'detail': 'Success'}
