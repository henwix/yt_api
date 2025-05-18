from abc import (
    ABC,
    abstractmethod,
)
from datetime import timedelta
from typing import (
    Iterable,
    Tuple,
)

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.apps.channels.models import Channel

from ..models import (
    Playlist,
    PlaylistItem,
    Video,
    VideoHistory,
    VideoLike,
    VideoView,
)


User = get_user_model()


class BaseVideoRepository(ABC):
    @abstractmethod
    def video_create(self, data: dict) -> None:
        ...

    @abstractmethod
    def get_video_by_upload_id(self, upload_id: str) -> Video:
        ...

    @abstractmethod
    def get_video_by_key(self, key: str) -> Video | None:
        ...

    @abstractmethod
    def update_video_after_upload(
        self,
        video_id: str,
        upload_id: str,
        s3_key: str,
    ) -> None:
        ...

    @abstractmethod
    def delete_video_by_id(self, video_id: str) -> None:
        ...

    @abstractmethod
    def get_channel(self, user: User) -> Channel | None:
        ...

    @abstractmethod
    def get_video_by_id(self, video_id: str) -> Video | None:
        ...

    @abstractmethod
    def like_get_or_create(self, channel: Channel, video: Video, is_like: bool) -> Tuple[VideoLike, bool]:
        ...

    @abstractmethod
    def like_delete(self, channel: Channel, video: Video) -> Tuple[int, dict]:
        ...

    @abstractmethod
    def last_view_exists(self, channel: Channel, video: Video, ip_address: str) -> bool:
        ...

    @abstractmethod
    def create_view(self, channel: Channel, video: Video, ip_address: str) -> None:
        ...

    @abstractmethod
    def get_videos_list(self) -> Iterable[Video]:
        ...


# TODO: refactor filters in repo using Q classes as method arguments
class ORMVideoRepository(BaseVideoRepository):
    def video_create(self, data: dict) -> None:
        return Video.objects.create(**data)

    def get_video_by_upload_id(self, upload_id: str) -> Video | None:
        return Video.objects.filter(upload_id=upload_id).first()

    def get_video_by_key(self, key: str) -> Video | None:
        return Video.objects.filter(s3_key=key).first()

    def update_video_after_upload(self, video_id: str, upload_id: str, s3_key: str) -> None:
        Video.objects.filter(
            video_id=video_id,
            upload_id=upload_id,
        ).update(
            s3_key=s3_key,
            upload_id=None,
            upload_status=Video.UploadStatus.FINISHED,
        )

    def delete_video_by_id(self, video_id: str) -> None:
        Video.objects.filter(video_id=video_id).delete()

    def get_channel(self, user: User) -> Channel | None:
        return Channel.objects.filter(user=user).first()

    def get_video_by_id(self, video_id: str) -> Video | None:
        return Video.objects.filter(video_id=video_id).first()

    def like_get_or_create(
        self,
        channel: Channel,
        video: Video,
        is_like: bool,
    ) -> Tuple[VideoLike, bool]:
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


class BaseVideoHistoryRepository(ABC):
    @abstractmethod
    def get_or_create_history_item(self, video: Video, channel: Channel) -> dict:
        ...

    @abstractmethod
    def delete_history_item(self, video: Video, channel: Channel) -> dict:
        ...

    @abstractmethod
    def update_watch_time(self, history_item: VideoHistory) -> None:
        ...


class ORMVideoHistoryRepository(BaseVideoHistoryRepository):
    def get_or_create_history_item(self, video: Video, channel: Channel) -> dict:
        return VideoHistory.objects.get_or_create(channel=channel, video=video)

    def delete_history_item(self, video: Video, channel: Channel) -> dict:
        return VideoHistory.objects.filter(channel=channel, video_id=video).delete()

    def update_watch_time(self, history_item: VideoHistory) -> None:
        history_item.watched_at = timezone.now()
        history_item.save(update_fields=['watched_at'])


class BasePlaylistRepository(ABC):
    @abstractmethod
    def get_all_playlists(self) -> Iterable[Playlist]:
        ...

    @abstractmethod
    def get_playlist_by_id(self, playlist_id: str) -> Playlist | None:
        ...

    @abstractmethod
    def playlist_item_get_or_create(self, playlist: Playlist, video: Video) -> PlaylistItem | None:
        ...

    @abstractmethod
    def playlist_item_delete(self, playlist: Playlist, video: Video) -> dict:
        ...


class ORMPlaylistRepository(BasePlaylistRepository):
    def get_all_playlists(self) -> Iterable[Playlist]:
        return Playlist.objects.all()

    def get_playlist_by_id(self, playlist_id: str) -> Playlist | None:
        return Playlist.objects.filter(id=playlist_id).first()

    def playlist_item_get_or_create(self, playlist: Playlist, video: Video) -> PlaylistItem | None:
        return PlaylistItem.objects.get_or_create(playlist=playlist, video=video)

    def playlist_item_delete(self, playlist: Playlist, video: Video) -> dict:
        return PlaylistItem.objects.filter(playlist=playlist, video=video).delete()
