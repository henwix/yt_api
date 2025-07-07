from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from django.conf import settings

from core.apps.users.entities import UserEntity
from core.apps.users.repositories.oauth2 import BaseOAuth2Repository


@dataclass
class BaseOAuth2Service(ABC):
    oauth2_repository: BaseOAuth2Repository

    @abstractmethod
    def get_connected_providers_as_dict(self, user: UserEntity) -> dict:
        ...


class OAuth2Service(BaseOAuth2Service):
    def get_connected_providers_as_dict(self, user: UserEntity) -> dict:
        connected_providers = self.oauth2_repository.get_connected_providers(user=user)
        connected_providers_names = [i.provider for i in connected_providers]

        response = {}
        for k, v in settings.OAUTH2_ALLOWED_BACKENDS.items():
            response[k] = True if v in connected_providers_names else False

        return {'connected': response}
