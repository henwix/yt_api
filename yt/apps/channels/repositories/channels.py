from abc import ABC, abstractmethod
from typing import Iterable

from django.db import transaction
from django.shortcuts import get_object_or_404

from ..models import Channel, SubscriptionItem


class BaseChannelRepository(ABC):
    @abstractmethod
    def get_channel(self, user) -> Channel:
        pass

    @abstractmethod
    def delete_channel(self, user):
        pass


class ORMChannelRepository(BaseChannelRepository):
    def get_channel(self, user) -> Channel:
        return get_object_or_404(Channel, user=user)

    def delete_channel(self, user):
        user.delete()


class BaseChannelSubsRepository(ABC):
    @abstractmethod
    def get_subscriber_list(self) -> Iterable[SubscriptionItem]:
        pass


class ORMChannelSubsRepository(BaseChannelSubsRepository):
    def get_subscriber_list(self, channel) -> Iterable[SubscriptionItem]:
        return SubscriptionItem.objects.filter(subscribed_to=channel).select_related('subscriber', 'subscribed_to')


class BaseChannelAvatarRepository(ABC):
    @abstractmethod
    def delete_avatar(self, channel):
        pass


class ChannelAvatarRepository(BaseChannelAvatarRepository):
    def delete_avatar(self, channel):
        with transaction.atomic():
            channel.channel_avatar.delete()
            channel.channel_avatar = None
            channel.save()
