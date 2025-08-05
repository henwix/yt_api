from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.reports.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class ReportLimitError(ServiceException):
    default_code = ErrorCodes.REPORT_LIMIT
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    video_id: str
    channel_slug: str
