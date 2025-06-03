from abc import (
    ABC,
    abstractmethod,
)
from datetime import timedelta
from typing import Iterable

from django.utils import timezone

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.videos.converters.likes import video_like_to_entity
from core.apps.videos.converters.playlists import (
    playlist_item_to_entity,
    playlist_to_entity,
)
from core.apps.videos.converters.video_history import (
    video_history_from_entity,
    video_history_to_entity,
)
from core.apps.videos.converters.videos import (
    video_from_entity,
    video_to_entity,
)
from core.apps.videos.entities.likes import VideoLikeEntity
from core.apps.videos.entities.playlists import (
    PlaylistEntity,
    PlaylistItemEntity,
)
from core.apps.videos.entities.video_history import VideoHistoryEntity
from core.apps.videos.entities.videos import VideoEntity
from core.apps.videos.models import (
    Playlist,
    PlaylistItem,
    Video,
    VideoHistory,
    VideoLike,
    VideoView,
)


#  TODO: separate video repo and video_like repo
class BaseVideoRepository(ABC):
    @abstractmethod
    def video_create(self, video_entity: VideoEntity) -> None:
        ...

    @abstractmethod
    def get_video_by_upload_id(self, upload_id: str) -> VideoEntity | None:
        ...

    @abstractmethod
    def get_video_by_key(self, key: str) -> VideoEntity | None:
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
    def get_video_by_id_or_none(self, video_id: str) -> VideoEntity | None:
        ...

    @abstractmethod
    def like_get_or_create(
        self,
        channel: ChannelEntity,
        video: VideoEntity,
        is_like: bool,
    ) -> tuple[VideoLikeEntity, bool]:
        ...

    @abstractmethod
    def like_delete(self, channel: ChannelEntity, video: VideoEntity) -> bool:
        ...

    @abstractmethod
    def update_is_like_field(self, like: VideoLikeEntity, is_like: bool) -> None:
        ...

    @abstractmethod
    def last_view_exists(self, channel: ChannelEntity, video: VideoEntity, ip_address: str) -> bool:
        ...

    @abstractmethod
    def create_view(self, channel: ChannelEntity, video: VideoEntity, ip_address: str) -> None:
        ...

    @abstractmethod
    def get_videos_list(self) -> Iterable[Video]:
        ...


# TODO: refactor filters in repo using Q classes as method arguments
class ORMVideoRepository(BaseVideoRepository):
    def video_create(self, video_entity: VideoEntity) -> None:
        return video_from_entity(video_entity).save()

    def get_video_by_upload_id(self, upload_id: str) -> VideoEntity | None:
        video_dto = Video.objects.filter(upload_id=upload_id).first()
        return video_to_entity(video_dto) if video_dto else None

    def get_video_by_key(self, key: str) -> VideoEntity | None:
        video_dto = Video.objects.filter(s3_key=key).first()
        return video_to_entity(video_dto) if video_dto else None

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

    def get_video_by_id_or_none(self, video_id: str) -> VideoEntity | None:
        video_dto = Video.objects.filter(video_id=video_id).first()
        return video_to_entity(video_dto) if video_dto else None

    def like_get_or_create(
        self,
        channel: ChannelEntity,
        video: VideoEntity,
        is_like: bool,
    ) -> tuple[VideoLikeEntity, bool]:
        like, created = VideoLike.objects.get_or_create(
            channel_id=channel.id,
            video_id=video.id,
            defaults={
                'is_like': is_like,
            },
        )

        return video_like_to_entity(like), created

    def like_delete(self, channel: ChannelEntity, video: VideoEntity) -> bool:
        deleted, _ = VideoLike.objects.filter(channel_id=channel.id, video_id=video.id).delete()
        return True if deleted else False

    def update_is_like_field(self, like: VideoLikeEntity, is_like: bool) -> None:
        VideoLike.objects.filter(pk=like.id).update(is_like=is_like)

    def last_view_exists(self, channel: ChannelEntity, video: VideoEntity, ip_address: str) -> bool:
        return VideoView.objects.filter(
            # FIXME: проверить, как доходит отсюда видео при условии, что юзер аноним. не вылетает ли ошибка в сервисе
            channel_id=channel.id if channel else None,
            video_id=video.id,
            ip_address=ip_address if ip_address else None,
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).exists()

    def create_view(self, channel: ChannelEntity, video: VideoEntity, ip_address: str) -> None:
        VideoView.objects.create(
            channel_id=channel.id,
            video_id=video.id,
            ip_address=ip_address,
        )

    def get_videos_list(self) -> Iterable[Video]:
        return Video.objects.all()


class BaseVideoHistoryRepository(ABC):
    @abstractmethod
    def get_or_create_history_item(self, video: VideoEntity, channel: ChannelEntity) -> tuple[VideoHistoryEntity, bool]:
        ...

    @abstractmethod
    def delete_history_item(self, video: VideoEntity, channel: ChannelEntity) -> bool:
        ...

    @abstractmethod
    def update_watch_time(self, video_history: VideoHistoryEntity) -> None:
        ...


class ORMVideoHistoryRepository(BaseVideoHistoryRepository):
    def get_or_create_history_item(self, video: VideoEntity, channel: ChannelEntity) -> tuple[VideoHistoryEntity, bool]:
        video_history_dto, created = VideoHistory.objects.get_or_create(channel_id=channel.id, video_id=video.id)
        return video_history_to_entity(video_history_dto), created

    def delete_history_item(self, video: VideoEntity, channel: ChannelEntity) -> bool:
        deleted, _ = VideoHistory.objects.filter(channel_id=channel.id, video_id=video.id).delete()
        return True if deleted else False

    def update_watch_time(self, video_history: VideoHistoryEntity) -> None:
        video_history_dto = video_history_from_entity(video_history)
        video_history_dto.watched_at = timezone.now()
        video_history_dto.save(update_fields=['watched_at'])


class BasePlaylistRepository(ABC):
    @abstractmethod
    def get_all_playlists(self) -> Iterable[Playlist]:
        ...

    @abstractmethod
    def get_playlist_by_id(self, playlist_id: str) -> PlaylistEntity | None:
        ...

    @abstractmethod
    def playlist_item_get_or_create(self, playlist: PlaylistEntity, video: VideoEntity) -> tuple[PlaylistItem, bool]:
        ...

    @abstractmethod
    def playlist_item_delete(self, playlist: PlaylistEntity, video: VideoEntity) -> bool:
        ...


class ORMPlaylistRepository(BasePlaylistRepository):
    def get_all_playlists(self) -> Iterable[Playlist]:
        return Playlist.objects.all()

    def get_playlist_by_id(self, playlist_id: str) -> PlaylistEntity | None:
        playlist_dto = Playlist.objects.filter(id=playlist_id).first()
        return playlist_to_entity(playlist_dto) if playlist_dto else None

    def playlist_item_get_or_create(
        self,
        playlist: PlaylistEntity,
        video: VideoEntity,
    ) -> tuple[PlaylistItemEntity, bool]:
        playlist_item_dto, created = PlaylistItem.objects.get_or_create(playlist_id=playlist.id, video_id=video.id)
        return playlist_item_to_entity(playlist_item_dto), created

    def playlist_item_delete(self, playlist: PlaylistEntity, video: VideoEntity) -> bool:
        deleted, _ = PlaylistItem.objects.filter(playlist_id=playlist.id, video_id=video.id).delete()
        return True if deleted else False
