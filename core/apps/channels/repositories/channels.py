from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from django.db.models import (
    Count,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
)

from core.apps.channels.converters.channels import (
    channel_from_entity,
    channel_to_entity,
)
from core.apps.channels.converters.subscriptions import sub_to_entity
from core.apps.channels.entities.channels import ChannelEntity
from core.apps.channels.entities.subscriptions import SubscriptionItemEntity
from core.apps.channels.models import (
    Channel,
    SubscriptionItem,
)
from core.apps.users.converters.users import user_from_entity
from core.apps.users.entities import UserEntity
from core.apps.videos.models import Video


class BaseChannelRepository(ABC):
    @abstractmethod
    def channel_exists(self, id: int) -> bool:
        ...

    @abstractmethod
    def is_slug_exists(self, slug: str) -> bool:
        ...

    @abstractmethod
    def channel_create(self, channel_entity: ChannelEntity) -> ChannelEntity:
        ...

    @abstractmethod
    def create_by_data(self, data: dict) -> ChannelEntity:
        ...

    @abstractmethod
    def get_channel_by_user_or_none(self, user: UserEntity) -> ChannelEntity | None:
        ...

    @abstractmethod
    def get_channel_by_user_id_or_none(self, user_id: int) -> ChannelEntity | None:
        ...

    @abstractmethod
    def get_channel_by_slug(self, slug: str) -> ChannelEntity | None:
        ...

    @abstractmethod
    def delete_channel_by_user(self, user: UserEntity) -> None:
        ...

    @abstractmethod
    def set_avatar_s3_key(self, channel: ChannelEntity, avatar_s3_key: str | None) -> None:
        ...


class ORMChannelRepository(BaseChannelRepository):
    def channel_exists(self, id: int) -> bool:
        return Channel.objects.filter(pk=id).exists()

    def is_slug_exists(self, slug: str) -> bool:
        return Channel.objects.filter(slug=slug).exists()

    def channel_create(self, channel_entity: ChannelEntity) -> ChannelEntity:
        channel_dto = Channel.objects.create(**channel_entity.__dict__)
        return channel_to_entity(channel_dto)

    def create_by_data(self, data: dict) -> ChannelEntity:
        channel_dto = Channel.objects.create(**data)
        return channel_to_entity(channel_dto)

    def get_channel_by_user_or_none(self, user: UserEntity) -> ChannelEntity | None:
        channel_dto = Channel.objects.filter(user_id=user.id).first()
        return channel_to_entity(channel_dto) if channel_dto else None

    def get_channel_by_user_id_or_none(self, user_id: int) -> ChannelEntity | None:
        channel_dto = Channel.objects.filter(user_id=user_id).first()
        return channel_to_entity(channel_dto) if channel_dto else None

    def get_channel_by_slug(self, slug) -> ChannelEntity | None:
        channel_dto = Channel.objects.filter(slug=slug).first()
        return channel_to_entity(channel_dto) if channel_dto else None

    def delete_channel_by_user(self, user: UserEntity) -> None:
        user_from_entity(user).delete()

    def set_avatar_s3_key(self, channel: ChannelEntity, avatar_s3_key: str | None) -> None:
        channel_dto: Channel = channel_from_entity(channel)
        channel_dto.avatar_s3_key = avatar_s3_key
        channel_dto.save()


class BaseChannelSubsRepository(ABC):
    @abstractmethod
    def get_subscriber_list(self, channel: ChannelEntity) -> Iterable[SubscriptionItem]:
        ...


class ORMChannelSubsRepository(BaseChannelSubsRepository):
    def get_subscriber_list(self, channel: ChannelEntity) -> Iterable[SubscriptionItem]:
        return SubscriptionItem.objects.filter(subscribed_to_id=channel.id)


class BaseChannelMainRepository(ABC):
    @abstractmethod
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        ...


class ORMChannelMainRepository(BaseChannelMainRepository):
    def get_channel_main_page_list(self) -> Iterable[Channel]:
        second_qs = (
            Video.objects.select_related('author')
            .filter(
                author__slug=OuterRef('author__slug'),
                status=Video.VideoStatus.PUBLIC,
                upload_status=Video.UploadStatus.FINISHED,
            )
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
                ),
            )
        )
        return qs


class BaseChannelAboutRepository(ABC):
    @abstractmethod
    def get_channel_about_list(self) -> Iterable[Channel]:
        ...


class ORMChannelAboutRepository(BaseChannelAboutRepository):
    def get_channel_about_list(self) -> Iterable[Channel]:
        qs = (
            Channel.objects.all()
            .select_related('user')
            .annotate(
                total_views=Count('videos__views', distinct=True),
                total_videos=Count(
                    'videos',
                    filter=Q(
                        videos__status=Video.VideoStatus.PUBLIC,
                        videos__upload_status=Video.UploadStatus.FINISHED,
                    ),
                    distinct=True,
                ),
                total_subs=Count('followers', distinct=True),
            )
        )
        return qs


class BaseSubscriptionRepository(ABC):
    @abstractmethod
    def get_or_create_sub(
        self,
        subscriber: ChannelEntity,
        subscribed_to: ChannelEntity,
    ) -> tuple[SubscriptionItemEntity, bool]:
        ...

    @abstractmethod
    def delete_sub(self, subscriber: ChannelEntity, subscribed_to: ChannelEntity) -> bool:
        ...


class ORMSubscriptionRepository(BaseSubscriptionRepository):
    def get_or_create_sub(
        self,
        subscriber: ChannelEntity,
        subscribed_to: ChannelEntity,
    ) -> tuple[SubscriptionItemEntity, bool]:
        subscription_dto, created = SubscriptionItem.objects.get_or_create(
            subscriber_id=subscriber.id, subscribed_to_id=subscribed_to.id,
        )

        return sub_to_entity(subscription_dto), created

    def delete_sub(
        self,
        subscriber: ChannelEntity,
        subscribed_to: ChannelEntity,
    ) -> bool:
        deleted, _ = SubscriptionItem.objects.filter(
            subscriber_id=subscriber.id,
            subscribed_to_id=subscribed_to.id,
        ).delete()

        return True if deleted else False
