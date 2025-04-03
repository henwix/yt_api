import pytest
from punq import Container

from core.apps.reports.services.reports import BaseVideoReportsService


@pytest.fixture
def report_service(container: Container) -> BaseVideoReportsService:
    return container.resolve(BaseVideoReportsService)
