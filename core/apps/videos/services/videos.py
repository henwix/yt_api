from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Tuple

from django.contrib.auth.models import User
from django.db.models import Count, Q

from apps.channels.models import Channel

from ..exceptions.videos import LikeNotFound, VideoNotFound, ViewExistsError
from ..models import Video
from ..repositories.videos import BaseVideoRepository


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
        return self.repository.get_video(video_id)

    def _user_and_video_validate(self, user, video_id) -> Tuple[Channel | None, Video | None]:
        channel, video = self._get_channel(user), self._get_video(video_id)

        if not video:
            raise VideoNotFound(video_id=video_id)

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
            raise LikeNotFound(channel_slug=channel.slug, video_id=video.video_id)

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
                comments_count=Count('comments'),
                subs_count=Count('author__followers', distinct=True),
            )
        )

    def get_all_videos(self) -> Iterable[Video]:
        return self.repository.get_videos_list()
