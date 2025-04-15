import os
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
from django.db.models import (
    Count,
    Q,
)

from core.apps.channels.models import Channel
from core.apps.channels.repositories.channels import BaseChannelRepository
from core.apps.common.services.boto_client import BaseBotoClientService
from core.apps.videos.exceptions.playlists import (
    PlaylistIdNotProvidedError,
    PlaylistNotFoundError,
    VideoNotInPlaylistError,
)

from ..exceptions.videos import (
    LikeNotFoundError,
    UnsupportedFileFormatError,
    VideoIdNotProvidedError,
    VideoNotFoundError,
    VideoNotFoundInHistoryError,
    ViewExistsError,
)
from ..models import (
    Playlist,
    Video,
)
from ..repositories.videos import (
    BasePlaylistRepository,
    BaseVideoHistoryRepository,
    BaseVideoRepository,
)


User = get_user_model()


@dataclass(eq=False)
class BaseVideoService(ABC):
    repository: BaseVideoRepository

    @abstractmethod
    def like_create(self, user: User, video_id: str, is_like: bool) -> dict: ...

    @abstractmethod
    def like_delete(self, user: User, video_id: str) -> dict: ...

    @abstractmethod
    def view_create(self, user: User, video_id: str, ip_address: str) -> dict: ...


class VideoService(BaseVideoService):
    def _get_channel(self, user: User) -> Channel | None:
        return self.repository.get_channel(user)

    def _get_video(self, video_id) -> Video | None:
        return self.repository.get_video_by_id(video_id)

    def _user_and_video_validate(self, user, video_id) -> Tuple[Channel | None, Video | None]:
        channel, video = self._get_channel(user), self._get_video(video_id)

        if not video:
            raise VideoNotFoundError(video_id=video_id)

        return channel, video

    def like_create(self, user: User, video_id: str, is_like: bool) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        like, created = self.repository.like_get_or_create(channel, video, is_like)

        if not created and like.is_like != is_like:
            like.is_like = is_like
            like.save()

        return {'status': 'Success', 'is_like': is_like}

    def like_delete(self, user: User, video_id: str) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        deleted, _ = self.repository.like_delete(channel, video)

        if not deleted:
            raise LikeNotFoundError(channel_slug=channel.slug, video_id=video.video_id)

        return {'status': 'Success'}

    def view_create(self, user: User, video_id: str, ip_address: str) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        last_view_exists = self.repository.last_view_exists(channel, video, ip_address)

        if last_view_exists:
            raise ViewExistsError(channel_slug=channel.slug, video_id=video.video_id)

        self.repository.create_view(channel, video, ip_address)
        return {'status': 'Success'}

    def get_videos_for_listing(self) -> Iterable[Video]:
        return (
            self.repository.get_videos_list()
            .select_related('author')
            .filter(status=Video.VideoStatus.PUBLIC)
            .annotate(views_count=Count('views', distinct=True))
        )

    def get_videos_for_retrieve(self) -> Iterable[Video]:
        return (
            self.repository.get_videos_list()
            .select_related('author')
            .annotate(
                views_count=Count('views', distinct=True),
                likes_count=Count('likes', filter=Q(likes__is_like=True), distinct=True),
                comments_count=Count('comments', distinct=True),
                subs_count=Count('author__followers', distinct=True),
            )
        )

    def get_all_videos(self) -> Iterable[Video]:
        return self.repository.get_videos_list()


@dataclass(eq=False)
class BaseVideoPresignedURLService(ABC):
    boto_service: BaseBotoClientService

    @abstractmethod
    def generate_url(self, filename: str) -> str: ...


class VideoPresignedURLService(BaseVideoPresignedURLService):
    def generate_url(self, filename: str) -> str:
        s3_client = self.boto_service.get_s3_client()

        if filename and filename[-4:] not in ['.mp4', '.mkv']:
            raise UnsupportedFileFormatError(filename=filename)

        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': os.environ.get('AWS_STORAGE_BUCKET_NAME'),
                'Key': f'channel_avatars/{filename}',
            },
            ExpiresIn=120,
            HttpMethod='PUT',
        )

        return {'put_url': url}


@dataclass
class BaseVideoHistoryService(ABC):
    channel_repository: BaseChannelRepository
    video_repository: BaseVideoRepository
    history_repository: BaseVideoHistoryRepository

    @abstractmethod
    def add_video_in_history(self, user: User, video_id: str) -> dict: ...

    @abstractmethod
    def delete_video_from_history(self, user: User, video_id: str) -> dict: ...


class VideoHistoryService(BaseVideoHistoryService):
    def _validate_video_id_and_get_objects(self, video_id: str, user: User) -> Tuple[Channel, Video]:
        """Validate video_id and returns channel and video objects from
        database."""
        if not video_id:
            raise VideoIdNotProvidedError()

        channel = self.channel_repository.get_channel_by_user(user=user)
        video = self.video_repository.get_video_by_id(video_id=video_id)

        if not video:
            raise VideoNotFoundError(video_id=video_id)

        return channel, video

    def add_video_in_history(self, user: User, video_id: str) -> dict:
        channel, video = self._validate_video_id_and_get_objects(video_id, user)

        history_item, created = self.history_repository.get_or_create_history_item(video=video, channel=channel)

        if not created:
            self.history_repository.update_watch_time(history_item=history_item)
            return {'status': 'Video already exists in history, watched_at has been updated'}

        return {'status': 'Video added in history'}

    def delete_video_from_history(self, user: User, video_id: str) -> dict:
        channel, video = self._validate_video_id_and_get_objects(video_id, user)

        deleted, _ = self.history_repository.delete_history_item(video=video, channel=channel)

        if not deleted:
            raise VideoNotFoundInHistoryError(video_id=video_id, channel_slug=channel.slug)

        return {'status': 'Video successfully deleted from history'}


@dataclass
class BaseVideoPlaylistService(ABC):
    video_repository: BaseVideoRepository
    playlist_repository: BasePlaylistRepository

    @abstractmethod
    def add_video_in_playlist(self, playlist_id: str, video_id: str) -> dict: ...

    @abstractmethod
    def delete_video_from_playlist(self, playlist_id: str, video_id: str) -> dict: ...


@dataclass
class VideoPlaylistService(BaseVideoPlaylistService):
    channel_repository: BaseChannelRepository

    def _validate_data_and_return_objects(self, playlist_id: str, video_id: str):
        if not video_id:
            raise VideoIdNotProvidedError()
        if not playlist_id:
            raise PlaylistIdNotProvidedError()

        playlist = self.playlist_repository.get_playlist_by_id(playlist_id=playlist_id)
        video = self.video_repository.get_video_by_id(video_id=video_id)

        if not video:
            raise VideoNotFoundError(video_id=video_id)
        if not playlist:
            raise PlaylistNotFoundError(playlist_id=playlist_id)

        return playlist, video

    def add_video_in_playlist(self, playlist_id: str, video_id: str) -> dict:
        playlist, video = self._validate_data_and_return_objects(playlist_id, video_id)

        _, created = self.playlist_repository.playlist_item_get_or_create(playlist=playlist, video=video)

        if created:
            return {'status': 'Video added in playlist'}
        return {'status': 'Video already exists in that playlist'}

    def delete_video_from_playlist(self, playlist_id: str, video_id: str) -> dict:
        playlist, video = self._validate_data_and_return_objects(playlist_id, video_id)

        deleted, _ = self.playlist_repository.playlist_item_delete(playlist=playlist, video=video)

        if not deleted:
            raise VideoNotInPlaylistError()
        return {'status': 'Video successfully deleted from playlist'}

    def get_playlists_for_listing(self, user: User) -> Iterable[Playlist]:
        queryset = self.playlist_repository.get_all_playlists()
        channel = self.channel_repository.get_channel_by_user(user=user)
        return (
            queryset.filter(channel=channel)
            .prefetch_related('videos__author')
            .select_related('channel')
            .annotate(videos_count=Count('videos', distinct=True))
        )

    def get_playlists_for_retrieving(self) -> Iterable[Playlist]:
        queryset = self.playlist_repository.get_all_playlists()

        return (
            queryset.prefetch_related('videos__author')
            .select_related('channel')
            .annotate(videos_count=Count('videos', distinct=True))
        )
