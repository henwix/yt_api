import punq
import pytest

from core.apps.reports.use_cases.create import CreateReportUseCase


@pytest.fixture
def create_report_use_case(container: punq.Container) -> CreateReportUseCase:
    return container.resolve(CreateReportUseCase)
