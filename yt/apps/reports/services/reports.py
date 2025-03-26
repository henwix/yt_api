from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from ..models import VideoReport
from ..repositories.reports import BaseVideoReportsRepository


@dataclass(eq=False)
class BaseVideoReportsService(ABC):
    repository: BaseVideoReportsRepository

    @abstractmethod
    def get_reports(self) -> Iterable[VideoReport]:
        pass


class VideoReportsService(BaseVideoReportsService):
    def get_reports(self, action: str) -> Iterable[VideoReport]:
        if action in ['retrieve', 'list']:
            return self.repository.get_reports_related()
        return self.repository.get_reports()
