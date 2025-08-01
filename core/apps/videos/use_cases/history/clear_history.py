from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.entities import UserEntity
from core.apps.videos.services.videos import BaseVideoHistoryService


@dataclass
class ClearVideoHistoryUseCase:
    channel_service: BaseChannelService
    history_service: BaseVideoHistoryService

    def execute(self, user: UserEntity) -> dict:
        channel = self.channel_service.get_channel_by_user_or_404(user=user)

        deleted = self.history_service.clear_history(channel=channel)
        if deleted:
            return {'status': 'history cleared'}
        return {'status': 'history is empty'}
