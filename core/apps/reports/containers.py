import punq

from core.apps.reports.repositories.reports import BaseVideoReportsRepository, ORMVideoReportRepository
from core.apps.reports.services.reports import BaseVideoReportsService, VideoReportsService


def initialize_reports(container: punq.Container) -> None:
    # repositories
    container.register(BaseVideoReportsRepository, ORMVideoReportRepository)

    # services
    container.register(BaseVideoReportsService, VideoReportsService)
