from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.reports.converters.reports import report_to_entity
from core.apps.reports.entities.reports import VideoReportEntity
from core.apps.reports.models import VideoReport
from core.apps.videos.entities.videos import VideoEntity


class BaseVideoReportsRepository(ABC):
    @abstractmethod
    def get_reports(self) -> Iterable[VideoReport]: ...

    @abstractmethod
    def create_report(
        self,
        video: VideoEntity,
        author: ChannelEntity,
        reason: str,
        description: str,
    ) -> VideoReportEntity: ...

    @abstractmethod
    def get_user_reports_count(self, video: VideoEntity, channel: ChannelEntity) -> int: ...


class ORMVideoReportRepository(BaseVideoReportsRepository):
    def get_reports(self) -> Iterable[VideoReport]:
        return VideoReport.objects.all()

    def create_report(
        self,
        video: VideoEntity,
        author: ChannelEntity,
        reason: str,
        description: str,
    ) -> VideoReportEntity:
        report_dto = VideoReport.objects.create(
            video_id=video.id,
            author_id=author.id,
            reason=reason,
            description=description,
        )
        return report_to_entity(report_dto)

    def get_user_reports_count(self, video: VideoEntity, channel: ChannelEntity) -> int:
        return VideoReport.objects.filter(video_id=video.id, author_id=channel.id).count()
