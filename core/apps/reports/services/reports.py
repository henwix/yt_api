from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from django.contrib.auth import get_user_model

from core.apps.channels.models import Channel
from core.apps.channels.repositories.channels import BaseChannelRepository
from core.apps.reports.exceptions.reports import ReportLimitError
from core.apps.videos.exceptions.videos import VideoNotFoundError
from core.apps.videos.models import Video
from core.apps.videos.repositories.videos import BaseVideoRepository

from ..models import VideoReport
from ..repositories.reports import BaseVideoReportsRepository


User = get_user_model()


@dataclass(eq=False)
class BaseVideoReportsService(ABC):
    report_repository: BaseVideoReportsRepository
    video_repository: BaseVideoRepository
    channel_repository: BaseChannelRepository

    @abstractmethod
    def get_report_list(self) -> Iterable[VideoReport]: ...

    @abstractmethod
    def create_report(self, video_id: str, user: User, reason: str, description: str) -> dict: ...


class VideoReportsService(BaseVideoReportsService):
    def _report_validation(self, video: Video, video_id: str, channel: Channel) -> None:
        if not video:
            raise VideoNotFoundError(video_id=video_id)

        if VideoReport.objects.filter(video=video, author=channel).count() >= 3:
            raise ReportLimitError(video_id=video_id, channel_slug=channel.slug)

    def get_report_list(self) -> Iterable[VideoReport]:
        return self.report_repository.get_reports()

    def create_report(self, video_id: str, user: User, reason: str, description: str) -> dict:
        video = self.video_repository.get_video_by_id(video_id)
        channel = self.channel_repository.get_channel_by_user(user)

        self._report_validation(video, video_id, channel)

        self.report_repository.create_report(video, channel, reason, description)
        return {'status': 'Successfully created'}

    def get_report_list_related(self) -> Iterable[VideoReport]:
        return self.report_repository.get_reports().select_related('video', 'author')
