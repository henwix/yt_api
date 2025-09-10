from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from django.db.models import (
    Count,
    Q,
)

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.channels.models import Channel
from core.apps.channels.repositories.channels import BaseChannelRepository
from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.entities import UserEntity
from core.apps.videos.converters.playlists import playlist_to_entity
from core.apps.videos.entities.playlists import PlaylistEntity
from core.apps.videos.entities.videos import VideoEntity
from core.apps.videos.exceptions.playlists import (
    PlaylistIdNotProvidedError,
    PlaylistNotFoundError,
    PlaylistPermissionError,
    VideoNotInPlaylistError,
)
from core.apps.videos.exceptions.upload import (
    VideoNotFoundByKeyError,
    VideoNotFoundByUploadIdError,
)
from core.apps.videos.exceptions.videos import (
    PrivateVideoOrUploadingError,
    PrivateVideoPermissionError,
    VideoAuthorNotMatchError,
    VideoIdNotProvidedError,
    VideoLikeNotFoundError,
    VideoNotFoundByVideoIdError,
    VideoNotFoundInHistoryError,
    ViewExistsError,
)
from core.apps.videos.models import (
    Playlist,
    Video,
    VideoHistory,
)
from core.apps.videos.repositories.videos import (
    BasePlaylistRepository,
    BaseVideoHistoryRepository,
    BaseVideoRepository,
)


class BaseVideoValidatorService(ABC):
    @abstractmethod
    def validate(self, video: VideoEntity | None, video_id: str) -> None:
        ...


class VideoExistsValidatorService(BaseVideoValidatorService):
    def validate(self, video: VideoEntity | None, video_id: str) -> None:
        if not video:
            raise VideoNotFoundByVideoIdError(video_id=video_id)


class BaseVideoAuthorValidatorService(ABC):
    @abstractmethod
    def validate(self, video: VideoEntity, author: ChannelEntity) -> None:
        ...


class VideoMatchAuthorValidatorService(BaseVideoAuthorValidatorService):
    def validate(self, video: Video, author: Channel) -> None:
        if not video.author_id == author.id:
            raise VideoAuthorNotMatchError(video_id=video.id, author_id=author.id)


class BasePrivateVideoPermissionValidatorService(ABC):
    @abstractmethod
    def validate(self, video: VideoEntity, channel: ChannelEntity | None) -> None:
        ...


class VideoPrivatePermissionValidatorService(BasePrivateVideoPermissionValidatorService):
    def validate(self, video: VideoEntity, channel: ChannelEntity | None) -> None:
        if video.status == Video.VideoStatus.PRIVATE and (channel is None or video.author_id != channel.id):
            raise PrivateVideoPermissionError(video_id=video.id, channel_id=channel.id if channel else 'AnonymousUser')


class BaseVideoPrivateOrUploadingValidatorService(ABC):
    @abstractmethod
    def validate(self, video: VideoEntity, channel: ChannelEntity) -> None:
        ...


class VideoPrivateOrUploadingValidatorService(BaseVideoPrivateOrUploadingValidatorService):
    def validate(self, video: VideoEntity, channel: ChannelEntity) -> None:
        """Raise an error if the video is PRIVATE or still UPLOADING."""
        if video.status == Video.VideoStatus.PRIVATE or video.upload_status == Video.UploadStatus.UPLOADING:
            raise PrivateVideoOrUploadingError(video_id=video.id, channel_id=channel.id)


@dataclass(eq=False)
class BaseVideoService(ABC):
    video_repository: BaseVideoRepository
    channel_repository: BaseChannelRepository
    channel_service: BaseChannelService
    validator_service: BaseVideoValidatorService

    @abstractmethod
    def video_create(self, video_entity: VideoEntity) -> None:
        ...

    @abstractmethod
    def get_video_by_upload_id(self, upload_id: str) -> VideoEntity:
        ...

    @abstractmethod
    def get_video_by_key(self, key: str) -> VideoEntity:
        ...

    @abstractmethod
    def get_video_by_id_with_reports_count(self, video_id: str) -> VideoEntity:
        ...

    @abstractmethod
    def get_video_by_id_or_404(self, video_id: str) -> VideoEntity:
        ...

    @abstractmethod
    def update_is_reported_field(self, video: VideoEntity, is_reported: bool) -> None:
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
    def like_create(self, user: UserEntity, video_id: str, is_like: bool) -> dict:
        ...

    @abstractmethod
    def like_delete(self, user: UserEntity, video_id: str) -> dict:
        ...

    @abstractmethod
    def view_create(self, user: UserEntity, video_id: str, ip_address: str) -> dict:
        ...


class ORMVideoService(BaseVideoService):
    def _user_and_video_validate(
        self,
        user: UserEntity,
        video_id: str,
    ) -> tuple[ChannelEntity | None, VideoEntity]:
        channel = self.channel_service.get_channel_by_user_or_none(user=user)
        video = self.video_repository.get_video_by_id_or_none(video_id)

        self.validator_service.validate(video=video, video_id=video_id)

        return channel, video

    def video_create(self, video_entity: VideoEntity) -> None:
        self.video_repository.video_create(video_entity=video_entity)

    def get_video_by_upload_id(self, upload_id: str) -> VideoEntity:
        video = self.video_repository.get_video_by_upload_id(upload_id=upload_id)
        if not video:
            raise VideoNotFoundByUploadIdError(upload_id=upload_id)
        return video

    def get_video_by_key(self, key: str) -> VideoEntity:
        video = self.video_repository.get_video_by_key(key=key)
        if not video:
            raise VideoNotFoundByKeyError(key=key)
        return video

    def get_video_by_id_with_reports_count(self, video_id: str) -> VideoEntity:
        video = self.video_repository.get_video_by_id_with_reports_count(video_id)

        if not video:
            raise VideoNotFoundByVideoIdError(video_id)
        return video

    def get_video_by_id_or_404(self, video_id: str) -> VideoEntity:
        video = self.video_repository.get_video_by_id_or_none(video_id=video_id)

        if not video:
            raise VideoNotFoundByVideoIdError(video_id=video_id)
        return video

    def update_is_reported_field(self, video: VideoEntity, is_reported: bool) -> None:
        self.video_repository.update_is_reported_field(video, is_reported)

    def update_video_after_upload(
        self,
        video_id: str,
        upload_id: str,
        s3_key: str,
    ) -> None:
        self.video_repository.update_video_after_upload(
            video_id=video_id,
            upload_id=upload_id,
            s3_key=s3_key,
        )

    def delete_video_by_id(self, video_id: str) -> None:
        self.video_repository.delete_video_by_id(video_id=video_id)

    def like_create(self, user: UserEntity, video_id: str, is_like: bool) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        like, created = self.video_repository.like_get_or_create(channel, video, is_like)

        if not created and like.is_like != is_like:
            self.video_repository.update_is_like_field(like, is_like)

        return {'detail': 'Success', 'is_like': is_like}

    def like_delete(self, user: UserEntity, video_id: str) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        deleted = self.video_repository.like_delete(channel, video)

        if not deleted:
            raise VideoLikeNotFoundError(channel_slug=channel.slug, video_id=video.id)

        return {'detail': 'Success'}

    def view_create(self, user: UserEntity, video_id: str, ip_address: str) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        last_view_exists = self.video_repository.last_view_exists(channel, video, ip_address)

        if last_view_exists:
            raise ViewExistsError(
                channel_slug=channel.slug if channel else 'AnonymousUser',
                video_id=video.id,
            )

        self.video_repository.create_view(channel, video, ip_address)
        return {'detail': 'Success'}

    def get_videos_for_listing(self) -> Iterable[Video]:
        return (
            self.video_repository.get_videos_list()
            .select_related('author')
            .filter(status=Video.VideoStatus.PUBLIC, upload_status=Video.UploadStatus.FINISHED)
            .annotate(views_count=Count('views', distinct=True))
        )

    def get_videos_for_retrieve(self) -> Iterable[Video]:
        return (
            self.video_repository.get_videos_list()
            .select_related('author')
            .filter(upload_status=Video.UploadStatus.FINISHED)
            .annotate(
                views_count=Count('views', distinct=True),
                likes_count=Count('likes', filter=Q(likes__is_like=True), distinct=True),
                comments_count=Count('comments', distinct=True),
                subs_count=Count('author__followers', distinct=True),
            )
        )

    def get_all_videos(self) -> Iterable[Video]:
        return self.video_repository.get_videos_list().filter(upload_status=Video.UploadStatus.FINISHED)


@dataclass
class BaseVideoHistoryService(ABC):
    channel_repository: BaseChannelRepository
    video_repository: BaseVideoRepository
    history_repository: BaseVideoHistoryRepository

    @abstractmethod
    def add_video_in_history(self, user: UserEntity, video_id: str) -> dict:
        ...

    @abstractmethod
    def delete_video_from_history(self, user: UserEntity, video_id: str) -> dict:
        ...

    @abstractmethod
    def get_channel_history(self, user: UserEntity) -> Iterable[VideoHistory]:
        ...

    @abstractmethod
    def get_history_for_retrieve(self, user: UserEntity) -> Iterable[VideoHistory]:
        ...

    @abstractmethod
    def clear_history(self, channel: ChannelEntity) -> bool:
        ...


class ORMVideoHistoryService(BaseVideoHistoryService):
    def _validate_video_id_and_get_objects(self, video_id: str, user: UserEntity) -> tuple[ChannelEntity, VideoEntity]:
        """Validate video_id and returns channel and video objects from
        database."""

        if not video_id:
            raise VideoIdNotProvidedError()

        channel = self.channel_repository.get_channel_by_user_or_none(user=user)
        video = self.video_repository.get_video_by_id_or_none(video_id=video_id)

        if not video:
            raise VideoNotFoundByVideoIdError(video_id=video_id)

        return channel, video

    def add_video_in_history(self, user: UserEntity, video_id: str) -> dict:
        channel, video = self._validate_video_id_and_get_objects(video_id, user)

        history_item, created = self.history_repository.get_or_create_history_item(video=video, channel=channel)

        if not created:
            self.history_repository.update_watch_time(video_history=history_item)
            return {'detail': 'Video already exists in history, watched_at has been updated'}

        return {'detail': 'Success'}

    def delete_video_from_history(self, user: UserEntity, video_id: str) -> dict:
        channel, video = self._validate_video_id_and_get_objects(video_id, user)

        deleted = self.history_repository.delete_history_item(video=video, channel=channel)

        if not deleted:
            raise VideoNotFoundInHistoryError(video_id=video_id, channel_slug=channel.slug)

        return {'detail': 'Success'}

    def get_channel_history(self, user: UserEntity) -> Iterable[VideoHistory]:
        channel = self.channel_repository.get_channel_by_user_or_none(user=user)
        return self.history_repository.get_channel_history(channel=channel)

    def get_history_for_retrieve(self, user: UserEntity) -> Iterable[VideoHistory]:
        channel = self.channel_repository.get_channel_by_user_or_none(user=user)
        qs = self.history_repository.get_channel_history(channel=channel)
        return qs.select_related('video__author')

    def clear_history(self, channel: ChannelEntity) -> bool:
        return self.history_repository.clear_history(channel=channel)


class BasePlaylistPrivatePermissionValidatorService(ABC):
    @abstractmethod
    def validate(self, playlist: PlaylistEntity, channel: ChannelEntity | None) -> None:
        ...


class PlaylistPrivatePermissionValidatorService(BasePlaylistPrivatePermissionValidatorService):
    def validate(self, playlist: PlaylistEntity, channel: ChannelEntity | None) -> None:
        if playlist.status == Playlist.StatusChoices.PRIVATE and (channel is None or playlist.channel_id != channel.id):
            raise PlaylistPermissionError(
                playlist_id=playlist.id,
                channel_id=channel.id if channel else 'AnonymousUser',
            )


@dataclass
class BaseVideoPlaylistService(ABC):
    video_repository: BaseVideoRepository
    playlist_repository: BasePlaylistRepository
    channel_repository: BaseChannelRepository

    @abstractmethod
    def add_video_in_playlist(self, user: UserEntity, playlist_id: str, video_id: str) -> tuple[bool, dict]:
        ...

    @abstractmethod
    def delete_video_from_playlist(self, user: UserEntity, playlist_id: str, video_id: str) -> dict:
        ...

    @abstractmethod
    def get_playlist_videos(self, playlist_id: str) -> Iterable[Video]:
        ...

    @abstractmethod
    def get_playlist_by_id_or_error(self, playlist_id: str) -> PlaylistEntity:
        ...


@dataclass
class ORMVideoPlaylistService(BaseVideoPlaylistService):
    channel_repository: BaseChannelRepository

    def _validate_data_and_return_objects(self, user: UserEntity, playlist_id: str, video_id: str):
        if not video_id:
            raise VideoIdNotProvidedError()
        if not playlist_id:
            raise PlaylistIdNotProvidedError()

        playlist = self.playlist_repository.get_playlist_by_id(playlist_id=playlist_id)
        video = self.video_repository.get_video_by_id_or_none(video_id=video_id)

        if not video:
            raise VideoNotFoundByVideoIdError(video_id=video_id)
        if not playlist:
            raise PlaylistNotFoundError(playlist_id=playlist_id)

        channel = self.channel_repository.get_channel_by_user_or_none(user=user)
        if playlist.channel_id != channel.id:
            raise PlaylistPermissionError(playlist_id=playlist.id, channel_id=channel.id)

        return playlist, video

    def add_video_in_playlist(self, user: UserEntity, playlist_id: str, video_id: str) -> tuple[bool, dict]:
        playlist, video = self._validate_data_and_return_objects(user, playlist_id, video_id)

        _, created = self.playlist_repository.playlist_item_get_or_create(playlist=playlist, video=video)

        if created:
            return created, {'detail': 'Success'}
        return created, {'detail': 'Video already exists in that playlist'}

    def delete_video_from_playlist(self, user: UserEntity, playlist_id: str, video_id: str) -> dict:
        playlist, video = self._validate_data_and_return_objects(user, playlist_id, video_id)

        deleted = self.playlist_repository.playlist_item_delete(playlist=playlist, video=video)

        if not deleted:
            raise VideoNotInPlaylistError(playlist_id, video_id)
        return {'detail': 'Success'}

    def get_playlists_for_listing(self, user: UserEntity) -> Iterable[Playlist]:
        queryset = self.playlist_repository.get_all_playlists()
        channel = self.channel_repository.get_channel_by_user_or_none(user=user)
        return (
            queryset.filter(channel_id=channel.id)
            .prefetch_related('videos__author')
            .select_related('channel')
            .annotate(
                videos_count=Count(
                    'videos',
                    distinct=True,
                    filter=Q(
                        videos__status=Video.VideoStatus.PUBLIC,
                    ) & Q(videos__upload_status=Video.UploadStatus.FINISHED),
                ),
            )
        )

    def get_playlists_for_retrieving(self) -> Iterable[Playlist]:
        queryset = self.playlist_repository.get_all_playlists()

        return (
            queryset.prefetch_related('videos__author')
            .select_related('channel')
            .annotate(
                videos_count=Count(
                    'videos',
                    distinct=True,
                    filter=Q(
                        videos__status=Video.VideoStatus.PUBLIC,
                    ) & Q(videos__upload_status=Video.UploadStatus.FINISHED),
                ),
            )
        )

    def get_playlist_videos(self, playlist_id: str) -> Iterable[Video]:
        qs = self.video_repository.get_videos_list()

        return qs.filter(
            playlists=playlist_id,
        ).select_related('author')

    def get_playlist_by_id_or_error(self, playlist_id: str) -> PlaylistEntity:
        playlist = self.playlist_repository.get_all_playlists().filter(pk=playlist_id).first()

        if playlist is not None:
            return playlist_to_entity(playlist)
        raise PlaylistNotFoundError(playlist_id=playlist_id)
