from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from ..models import VideoReport
from ..repositories.reports import BaseVideoReportsRepository


@dataclass(eq=False)
class BaseVideoReportsService(ABC):
    repository: BaseVideoReportsRepository

    @abstractmethod
    def get_report_list(self) -> Iterable[VideoReport]: ...


class VideoReportsService(BaseVideoReportsService):
    def get_report_list(self) -> Iterable[VideoReport]:
        return self.repository.get_reports()

    def get_report_list_related(self) -> Iterable[VideoReport]:
        return self.repository.get_reports().select_related('video', 'author')
