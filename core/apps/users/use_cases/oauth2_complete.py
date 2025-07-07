from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.entities import UserEntity
from core.apps.users.services.users import BaseUserService


@dataclass
class OAuth2CompleteUseCase:
    user_service: BaseUserService
    channel_service: BaseChannelService

    def execute(self, retrieved_user: UserEntity, provider: str, is_authenticated: bool) -> dict:
        channel = self.channel_service.get_channel_by_user_or_none(user=retrieved_user)

        if not channel:
            self.channel_service.create_channel_by_user_info(user=retrieved_user)

        if not is_authenticated:
            return self.user_service.generate_jwt(user=retrieved_user)
        return {'status': f'{provider} successfully connected'}
