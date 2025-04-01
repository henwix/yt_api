import pytest
from apps.reports.services.reports import BaseVideoReportsService
from punq import Container


@pytest.fixture
def report_service(container: Container) -> BaseVideoReportsService:
    return container.resolve(BaseVideoReportsService)
