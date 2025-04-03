import random

import pytest

from core.apps.reports.services.reports import BaseVideoReportsService
from core.tests.factories.reports import VideoReportModelFactory


@pytest.mark.django_db
def test_get_reports_list_empty(report_service: BaseVideoReportsService):
    """Test report count zero with no products in database"""
    qs = report_service.get_report_list()
    assert qs.count() == 0


@pytest.mark.django_db
def test_get_reports_list_exists(report_service: BaseVideoReportsService):
    """Test all reports retrieved from database"""
    expected_value = random.randint(1, 15)
    VideoReportModelFactory.create_batch(size=expected_value)

    qs = report_service.get_report_list()
    assert qs.count() == expected_value
