from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from django.urls import reverse_lazy

from core.apps.users.constants import OAUTH2_ALLOWED_PROVIDERS
from core.apps.users.entities import UserEntity
from core.apps.users.exceptions.oauth2 import OAuth2NotImplementedProviderError
from core.apps.users.repositories.oauth2 import BaseOAuth2Repository


class BaseOAuth2ProviderValidatorService(ABC):
    @abstractmethod
    def validate(self, provider: str) -> None:
        ...


class OAuth2ProviderValidatorService(BaseOAuth2ProviderValidatorService):
    def validate(self, provider: str) -> None:
        if provider not in OAUTH2_ALLOWED_PROVIDERS:
            raise OAuth2NotImplementedProviderError(provider=provider)


@dataclass
class BaseOAuth2Service(ABC):
    oauth2_repository: BaseOAuth2Repository

    @abstractmethod
    def get_connected_providers_as_dict(self, user: UserEntity) -> dict:
        ...

    @abstractmethod
    def get_provider_by_name(self, provider: str) -> str | None:
        ...

    @abstractmethod
    def get_redirect_uri(self, provider: str) -> str:
        ...


class OAuth2Service(BaseOAuth2Service):
    def get_connected_providers_as_dict(self, user: UserEntity) -> dict:
        connected_providers = self.oauth2_repository.get_connected_providers(user=user)
        connected_providers_names = [i.provider for i in connected_providers]

        response = {}
        for k, v in OAUTH2_ALLOWED_PROVIDERS.items():
            response[k] = True if v in connected_providers_names else False

        return response

    def get_provider_by_name(self, provider: str) -> str:
        return OAUTH2_ALLOWED_PROVIDERS.get(provider)

    def get_redirect_uri(self, provider: str) -> str:
        return reverse_lazy('v1:users:oauth2-connect', kwargs={'provider': provider})
