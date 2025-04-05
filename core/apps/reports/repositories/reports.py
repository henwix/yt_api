from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.channels.models import Channel
from core.apps.videos.models import Video

from ..models import VideoReport


class BaseVideoReportsRepository(ABC):
    @abstractmethod
    def get_reports(self) -> Iterable[VideoReport]: ...

    @abstractmethod
    def create_report(self, video: Video, author: Channel, reason: str, description: str) -> VideoReport: ...


class ORMVideoReportRepository(BaseVideoReportsRepository):
    def get_reports(self) -> Iterable[VideoReport]:
        return VideoReport.objects.all()

    def create_report(self, video: Video, author: Channel, reason: str, description: str) -> VideoReport:
        return VideoReport.objects.create(video=video, author=author, reason=reason, description=description)
