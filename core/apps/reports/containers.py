import punq

from core.apps.reports.repositories.reports import (
    BaseVideoReportsRepository,
    ORMVideoReportRepository,
)
from core.apps.reports.services.reports import (
    BaseReportLimitByOneUserValidatorService,
    BaseVideoReportsService,
    ORMVideoReportsService,
    ReportLimitByOneUserValidatorService,
)
from core.apps.reports.use_cases.create import CreateReportUseCase


def init_reports(container: punq.Container) -> None:
    #  repositories
    container.register(BaseVideoReportsRepository, ORMVideoReportRepository)

    #  services
    container.register(BaseVideoReportsService, ORMVideoReportsService)
    container.register(
        BaseReportLimitByOneUserValidatorService,
        ReportLimitByOneUserValidatorService,
    )

    #  use cases
    container.register(CreateReportUseCase)
