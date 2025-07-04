from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.entities import UserEntity
from core.apps.users.services.users import BaseUserService


@dataclass
class SocialAuthUseCase:
    user_service: BaseUserService
    channel_service: BaseChannelService

    def execute(self, user: UserEntity) -> dict:
        channel = self.channel_service.get_channel_by_user_or_none(user=user)

        if not channel:
            self.channel_service.create_channel_by_user_info(user=user)

        return self.user_service.generate_jwt(user=user)
