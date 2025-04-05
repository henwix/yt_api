from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


@dataclass
class ReportLimitError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'You have reached limit of reports to this video. 3 reports by 1 user'}

    video_id: str
    channel_slug: str

    @property
    def message(self):
        return f"Channel {self.channel_slug} have reached limit of reports to video {self.video_id}"
