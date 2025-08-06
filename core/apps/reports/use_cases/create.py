from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.reports.services.reports import (
    BaseReportLimitByOneUserValidatorService,
    BaseVideoReportsService,
)
from core.apps.users.entities import UserEntity
from core.apps.videos.services.videos import (
    BaseVideoPrivateOrUploadingValidatorService,
    BaseVideoService,
)


@dataclass
class CreateReportUseCase:
    video_service: BaseVideoService
    channel_service: BaseChannelService
    report_service: BaseVideoReportsService
    video_validator: BaseVideoPrivateOrUploadingValidatorService
    report_validator: BaseReportLimitByOneUserValidatorService

    def execute(self, video_id: str, user: UserEntity, reason: str, description: str) -> dict[str, str]:
        video = self.video_service.get_video_by_id_with_reports_count(video_id=video_id)
        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        self.video_validator.validate(video=video, channel=channel)
        self.report_validator.validate(video=video, channel=channel)

        self.report_service.create_report(
            video=video,
            author=channel,
            reason=reason,
            description=description,
        )

        #  here we check if the video has >= 3 reports, including the new one we just created
        if video.reports_count + 1 >= 3 and not video.is_reported:
            self.video_service.update_is_reported_field(
                video=video,
                is_reported=True,
            )

        return {'detail': 'Success'}
