from dataclasses import dataclass

from core.apps.users.entities import UserEntity
from core.apps.users.services.oauth2 import BaseOAuth2Service


@dataclass
class OAuth2ConnectedProvidersUseCase:
    oauth2_service: BaseOAuth2Service

    def execute(self, user: UserEntity) -> dict:
        return self.oauth2_service.get_connected_providers_as_dict(user=user)
