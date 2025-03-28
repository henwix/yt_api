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
        qs = self.repository.get_reports()

        if action in ['retrieve', 'list']:
            return qs.select_related('video', 'author')
        return qs
