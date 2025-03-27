import punq

from apps.reports.repositories.reports import BaseVideoReportsRepository, ORMVideoReportRepository
from apps.reports.services.reports import BaseVideoReportsService, VideoReportsService


def initialize_reports(container: punq.Container) -> None:
    # repositories
    container.register(BaseVideoReportsRepository, ORMVideoReportRepository)

    # services
    container.register(BaseVideoReportsService, VideoReportsService)
