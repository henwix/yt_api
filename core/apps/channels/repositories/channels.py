from abc import ABC, abstractmethod
from typing import Dict, Iterable, Tuple

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, OuterRef, Prefetch, Q, Subquery

from apps.videos.models import Video

from ..models import Channel, SubscriptionItem


class BaseChannelRepository(ABC):
    @abstractmethod
    def get_channel_by_user(self, user: User) -> Channel | None:
        pass

    def get_channel_by_id(self, user_id: int) -> Channel | None:
        pass

    @abstractmethod
    def delete_channel(self, user: User) -> None:
        pass


class ORMChannelRepository(BaseChannelRepository):
    def get_channel_by_user(self, user: User) -> Channel | None:
        return Channel.objects.filter(user=user).first()

    def get_channel_by_id(self, user_id: int) -> Channel | None:
        return Channel.objects.filter(user_id=user_id).first()

    def delete_channel(self, user: User) -> None:
        user.delete()


class BaseChannelSubsRepository(ABC):
    @abstractmethod
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]:
        pass


class ORMChannelSubsRepository(BaseChannelSubsRepository):
    def get_subscriber_list(self, channel: Channel) -> Iterable[SubscriptionItem]:
        return SubscriptionItem.objects.filter(subscribed_to=channel).select_related('subscriber', 'subscribed_to')


class BaseChannelAvatarRepository(ABC):
    @abstractmethod
    def delete_avatar(self, channel: Channel) -> None:
        pass


class ORMChannelAvatarRepository(BaseChannelAvatarRepository):
    def delete_avatar(self, channel: Channel) -> None:
        with transaction.atomic():
            channel.channel_avatar.delete()
            channel.channel_avatar = None  # TODO: is this necessary or maybe just .delete enough?
            channel.save()


class BaseChannelMainRepository(ABC):
    @abstractmethod
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        pass


class ORMChannelMainRepository(BaseChannelMainRepository):
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        second_qs = (
            Video.objects.select_related('author')
            .filter(author__slug=OuterRef('author__slug'), status=Video.VideoStatus.PUBLIC)
            .order_by('-created_at')
            .values('pk')[:5]
        )
        qs = (
            Channel.objects.all()
            .annotate(subs_count=Count('followers', distinct=True))
            .prefetch_related(
                Prefetch(
                    'videos',
                    Video.objects.filter(pk__in=Subquery(second_qs))
                    .annotate(views_count=Count('views', distinct=True))
                    .order_by('-created_at'),
                )
            )
        )
        return qs


class BaseChannelAboutRepository(ABC):
    @abstractmethod
    def get_channel_about_list(self) -> Iterable[Channel]:
        pass


class ORMChannelAboutRepository(BaseChannelAboutRepository):
    def get_channel_about_list(self) -> Iterable[Channel]:
        qs = (
            Channel.objects.all()
            .select_related('user')
            .annotate(
                total_views=Count('videos__views', distinct=True),
                total_videos=Count('videos', filter=Q(videos__status=Video.VideoStatus.PUBLIC), distinct=True),
                total_subs=Count('followers', distinct=True),
            )
        )
        return qs


class BaseSubscriptionRepository(ABC):
    @abstractmethod
    def get_channels(self, user: User, slug: str) -> Tuple[Channel, Channel | None]:
        pass

    @abstractmethod
    def get_or_create_sub(self, subscriber: Channel, subscribed_to: Channel) -> Tuple[SubscriptionItem, bool]:
        pass

    @abstractmethod
    def delete_sub(self, subscriber: Channel, subscribed_to: Channel) -> Tuple[int, Dict[str, int]]:
        pass


class ORMSubscriptionRepository(BaseSubscriptionRepository):
    def get_channels(self, user: User, slug: str) -> Tuple[Channel, Channel | None]:
        subscriber = user.channel
        subscribed_to = Channel.objects.filter(slug=slug).first()
        return subscriber, subscribed_to

    def get_or_create_sub(self, subscriber: Channel, subscribed_to: Channel) -> Tuple[SubscriptionItem, bool]:
        return SubscriptionItem.objects.get_or_create(subscriber=subscriber, subscribed_to=subscribed_to)

    def delete_sub(self, subscriber: Channel, subscribed_to: Channel) -> Tuple[int, Dict[str, int]]:
        return SubscriptionItem.objects.filter(subscriber=subscriber, subscribed_to=subscribed_to).delete()
