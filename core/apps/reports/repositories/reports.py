from abc import ABC, abstractmethod
from typing import Iterable

from ..models import VideoReport


class BaseVideoReportsRepository(ABC):
    @abstractmethod
    def get_reports(self) -> Iterable[VideoReport]:
        pass


class ORMVideoReportRepository(BaseVideoReportsRepository):
    def get_reports(self) -> Iterable[VideoReport]:
        return VideoReport.objects.all()

    def get_reports_related(self) -> Iterable[VideoReport]:
        return VideoReport.objects.all().select_related('video', 'author')
