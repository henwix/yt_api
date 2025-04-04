from abc import (
    ABC,
    abstractmethod,
)
from datetime import timedelta
from typing import (
    Iterable,
    Tuple,
)

from django.contrib.auth.models import User
from django.utils import timezone

from core.apps.channels.models import Channel

from ..models import (
    Video,
    VideoLike,
    VideoView,
)


class BaseVideoRepository(ABC):
    @abstractmethod
    def get_channel(self, user: User) -> Channel | None: ...

    @abstractmethod
    def get_video(self, video_id: str) -> Video | None: ...

    @abstractmethod
    def like_get_or_create(self, channel: Channel, video: Video, is_like: bool) -> Tuple[VideoLike, bool]: ...

    @abstractmethod
    def like_delete(self, channel: Channel, video: Video) -> Tuple[int, dict]: ...

    @abstractmethod
    def last_view_exists(self, channel: Channel, video: Video, ip_address: str) -> bool: ...

    @abstractmethod
    def create_view(self, channel: Channel, video: Video, ip_address: str) -> None: ...

    def get_videos_list(self) -> Iterable[Video]: ...


class ORMVideoRepository(BaseVideoRepository):
    def get_channel(self, user: User) -> Channel | None:
        return Channel.objects.filter(user=user).first()

    def get_video(self, video_id: str) -> Video | None:
        return Video.objects.filter(video_id=video_id).first()

    def like_get_or_create(self, channel: Channel, video: Video, is_like: bool) -> Tuple[VideoLike, bool]:
        like, created = VideoLike.objects.get_or_create(
            channel=channel,
            video=video,
            defaults={
                'is_like': is_like,
            },
        )

        return like, created

    def like_delete(self, channel: Channel, video: Video) -> Tuple[int, dict]:
        return VideoLike.objects.filter(channel=channel, video=video).delete()

    def last_view_exists(self, channel: Channel, video: Video, ip_address: str) -> bool:
        return VideoView.objects.filter(
            channel=channel if channel else None,
            video=video,
            ip_address=ip_address if ip_address else None,
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).exists()

    def create_view(self, channel: Channel, video: Video, ip_address: str) -> None:
        VideoView.objects.create(
            channel=channel,
            video=video,
            ip_address=ip_address,
        )

    def get_videos_list(self) -> Iterable[Video]:
        return Video.objects.all()
