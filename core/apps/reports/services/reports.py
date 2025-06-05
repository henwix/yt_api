from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.channels.repositories.channels import BaseChannelRepository
from core.apps.reports.exceptions.reports import ReportLimitError
from core.apps.reports.models import VideoReport
from core.apps.reports.repositories.reports import BaseVideoReportsRepository
from core.apps.videos.entities.videos import VideoEntity
from core.apps.videos.repositories.videos import BaseVideoRepository


@dataclass
class BaseReportLimitByOneUserValidatorService(ABC):
    report_repository: BaseVideoReportsRepository

    @abstractmethod
    def validate(self, video: VideoEntity, channel: ChannelEntity) -> None:
        ...


class ReportLimitByOneUserValidatorService(BaseReportLimitByOneUserValidatorService):
    def validate(self, video: VideoEntity, channel: ChannelEntity) -> None:
        """Raise an error if the limit of reports by one user >= 3."""
        reports_count = self.report_repository.get_user_reports_count(video=video, channel=channel)
        if reports_count >= 3:
            raise ReportLimitError(video_id=video.id, channel_slug=channel.slug)


@dataclass(eq=False)
class BaseVideoReportsService(ABC):
    report_repository: BaseVideoReportsRepository
    video_repository: BaseVideoRepository
    channel_repository: BaseChannelRepository

    @abstractmethod
    def get_report_list(self) -> Iterable[VideoReport]:
        ...

    @abstractmethod
    def create_report(self, video: VideoEntity, author: ChannelEntity, reason: str, description: str) -> dict:
        ...


class ORMVideoReportsService(BaseVideoReportsService):
    def get_report_list(self) -> Iterable[VideoReport]:
        return self.report_repository.get_reports()

    def create_report(self, video: VideoEntity, author: ChannelEntity, reason: str, description: str) -> None:
        self.report_repository.create_report(video, author, reason, description)

    def get_report_list_related(self) -> Iterable[VideoReport]:
        return self.report_repository.get_reports().select_related('video', 'author')
