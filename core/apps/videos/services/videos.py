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
from core.apps.videos.exceptions.upload import UnsupportedFileFormatError

from ..exceptions.videos import (
    VideoIdNotProvidedError,
    VideoLikeNotFoundError,
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


class BaseVideoValidatorService(ABC):
    @abstractmethod
    def validate(self, video: Video | None, video_id: str) -> None:
        ...


class VideoValidatorService(BaseVideoValidatorService):
    def validate(self, video: Video | None, video_id: str) -> None:
        if not video:
            raise VideoNotFoundError(video_id=video_id)


@dataclass(eq=False)
class BaseVideoService(ABC):
    video_repository: BaseVideoRepository
    channel_repository: BaseChannelRepository
    validator_service: BaseVideoValidatorService

    @abstractmethod
    def video_create_s3(self, validated_data: dict) -> None:
        ...

    @abstractmethod
    def delete_video_by_id(self, video_id: str) -> None:
        ...

    @abstractmethod
    def get_video_by_upload_id_and_author(self, author: Channel, upload_id: str) -> Video:
        ...

    @abstractmethod
    def like_create(self, user: User, video_id: str, is_like: bool) -> dict:
        ...

    @abstractmethod
    def like_delete(self, user: User, video_id: str) -> dict:
        ...

    @abstractmethod
    def view_create(self, user: User, video_id: str, ip_address: str) -> dict:
        ...


class ORMVideoService(BaseVideoService):
    def _user_and_video_validate(self, user, video_id) -> Tuple[Channel | None, Video | None]:
        channel = self.channel_repository.get_channel_by_user(user=user)
        video = self.video_repository.get_video_by_id(video_id)

        self.validator_service.validate(video=video, video_id=video_id)

        return channel, video

    def video_create_s3(self, validated_data: dict) -> None:
        self.video_repository.video_create_s3(validated_data=validated_data)

    def delete_video_by_id(self, video_id: str) -> None:
        self.video_repository.delete_video_by_id(video_id=video_id)

    def get_video_by_upload_id_and_author(self, author: Channel, upload_id: str) -> Video:
        return self.video_repository.get_video_by_upload_id_and_author(author=author, upload_id=upload_id)

    def like_create(self, user: User, video_id: str, is_like: bool) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        like, created = self.video_repository.like_get_or_create(channel, video, is_like)

        if not created and like.is_like != is_like:
            like.is_like = is_like
            like.save()

        return {'status': 'success', 'is_like': is_like}

    def like_delete(self, user: User, video_id: str) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        deleted, _ = self.video_repository.like_delete(channel, video)

        if not deleted:
            raise VideoLikeNotFoundError(channel_slug=channel.slug, video_id=video.video_id)

        return {'status': 'Success'}

    def view_create(self, user: User, video_id: str, ip_address: str) -> dict:
        channel, video = self._user_and_video_validate(user, video_id)

        last_view_exists = self.video_repository.last_view_exists(channel, video, ip_address)

        if last_view_exists:
            raise ViewExistsError(channel_slug=channel.slug, video_id=video.video_id)

        self.video_repository.create_view(channel, video, ip_address)
        return {'status': 'Success'}

    def get_videos_for_listing(self) -> Iterable[Video]:
        return (
            self.video_repository.get_videos_list()
            .select_related('author')
            .filter(status=Video.VideoStatus.PUBLIC)
            .annotate(views_count=Count('views', distinct=True))
        )

    def get_videos_for_retrieve(self) -> Iterable[Video]:
        return (
            self.video_repository.get_videos_list()
            .select_related('author')
            .annotate(
                views_count=Count('views', distinct=True),
                likes_count=Count('likes', filter=Q(likes__is_like=True), distinct=True),
                comments_count=Count('comments', distinct=True),
                subs_count=Count('author__followers', distinct=True),
            )
        )

    def get_all_videos(self) -> Iterable[Video]:
        return self.video_repository.get_videos_list()


@dataclass(eq=False)
class BaseVideoPresignedURLService(ABC):
    boto_service: BaseBotoClientService

    @abstractmethod
    def generate_url(self, filename: str) -> str: ...


class ORMVideoPresignedURLService(BaseVideoPresignedURLService):
    def generate_url(self, filename: str) -> str:
        s3_client = self.boto_service.get_s3_client()

        if filename and filename[-4:] not in ['.mp4', '.mkv', '.png', '.jpg']:
            raise UnsupportedFileFormatError(filename=filename)

        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.boto_service.get_bucket_name(),
                'Key': f'channel_avatars/{filename}',
            },
            # ExpiresIn=120,
            ExpiresIn=600,
            HttpMethod='PUT',
        )

        return {'put_url': url}


@dataclass
class BaseMultipartUploadVideoService(ABC):
    boto_service: BaseBotoClientService

    @abstractmethod
    def init_multipart_upload(self, filename: str) -> tuple:
        ...

    @abstractmethod
    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        ...

    @abstractmethod
    def generate_upload_part_url(self, key: str, upload_id: str, part_number: int):
        ...


@dataclass
class MultipartUploadVideoService(BaseMultipartUploadVideoService):
    def _get_client_and_bucket(self) -> tuple:
        s3_client = self.boto_service.get_s3_client()
        bucket = self.boto_service.get_bucket_name()

        return s3_client, bucket

    def init_multipart_upload(self, filename: str) -> tuple:
        s3_client, bucket = self._get_client_and_bucket()
        key = f'videos/{filename}'

        response = s3_client.create_multipart_upload(
            Bucket=bucket,
            Key=key,
        )

        return response.get('UploadId'), response.get('Key')

    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        s3_client, bucket = self._get_client_and_bucket()

        s3_client.abort_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
        )

    def generate_upload_part_url(
        self,
        key: str,
        upload_id: str,
        part_number: int,
    ) -> str:
        s3_client, bucket = self._get_client_and_bucket()

        url = s3_client.generate_presigned_url(
            ClientMethod='upload_part',
            Params={
                'Bucket': bucket,
                'Key': key,
                'UploadId': upload_id,
                'PartNumber': part_number,
            },
            ExpiresIn=600,
        )
        return url


@dataclass
class BaseVideoHistoryService(ABC):
    channel_repository: BaseChannelRepository
    video_repository: BaseVideoRepository
    history_repository: BaseVideoHistoryRepository

    @abstractmethod
    def add_video_in_history(self, user: User, video_id: str) -> dict: ...

    @abstractmethod
    def delete_video_from_history(self, user: User, video_id: str) -> dict: ...


class ORMVideoHistoryService(BaseVideoHistoryService):
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
    def add_video_in_playlist(self, playlist_id: str, video_id: str) -> dict:
        ...

    @abstractmethod
    def delete_video_from_playlist(self, playlist_id: str, video_id: str) -> dict:
        ...


@dataclass
class ORMVideoPlaylistService(BaseVideoPlaylistService):
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
