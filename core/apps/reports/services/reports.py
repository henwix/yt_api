from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from core.apps.channels.entities.channels import ChannelEntity
from core.apps.channels.repositories.channels import BaseChannelRepository
from core.apps.reports.exceptions.reports import ReportLimitError
from core.apps.reports.models import VideoReport
from core.apps.reports.repositories.reports import BaseVideoReportsRepository
from core.apps.users.entities import UserEntity
from core.apps.videos.entities.videos import VideoEntity
from core.apps.videos.exceptions.videos import VideoNotFoundByVideoIdError
from core.apps.videos.models import Video
from core.apps.videos.repositories.videos import BaseVideoRepository


@dataclass(eq=False)
class BaseVideoReportsService(ABC):
    report_repository: BaseVideoReportsRepository
    video_repository: BaseVideoRepository
    channel_repository: BaseChannelRepository

    @abstractmethod
    def get_report_list(self) -> Iterable[VideoReport]:
        ...

    @abstractmethod
    def create_report(self, video_id: str, user: UserEntity, reason: str, description: str) -> dict:
        ...


class ORMVideoReportsService(BaseVideoReportsService):
    def _report_validation(self, video: VideoEntity | None, video_id: str, channel: ChannelEntity) -> None:
        #  Here we check if the video is still uploading or private, the VideoNotFoundById error will be raised
        if not video or (
            video.upload_status == Video.UploadStatus.UPLOADING or video.status == Video.VideoStatus.PRIVATE
        ):
            raise VideoNotFoundByVideoIdError(video_id=video_id)

        #  Check if the user sent a report for the same video more than 3 times
        #  TODO: move to repository
        if VideoReport.objects.filter(video_id=video.id, author_id=channel.id).count() >= 3:
            raise ReportLimitError(video_id=video_id, channel_slug=channel.slug)

    def get_report_list(self) -> Iterable[VideoReport]:
        return self.report_repository.get_reports()

    # TODO: refactor with use case
    # TODO: set is_reported to True for video when number of reports > 3
    def create_report(self, video_id: str, user: UserEntity, reason: str, description: str) -> dict:
        video = self.video_repository.get_video_by_id_or_none(video_id)
        channel = self.channel_repository.get_channel_by_user_or_none(user)

        self._report_validation(video, video_id, channel)

        self.report_repository.create_report(video, channel, reason, description)
        return {'status': 'Successfully created'}

    def get_report_list_related(self) -> Iterable[VideoReport]:
        return self.report_repository.get_reports().select_related('video', 'author')
