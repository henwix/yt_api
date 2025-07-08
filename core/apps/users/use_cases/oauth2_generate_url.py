from dataclasses import dataclass

from social_django.strategy import DjangoStrategy
from social_django.utils import load_backend

from core.apps.users.services.oauth2 import (
    BaseOAuth2ProviderValidatorService,
    BaseOAuth2Service,
)


@dataclass
class OAuth2GenerateURLUseCase:
    provider_validator_service: BaseOAuth2ProviderValidatorService
    oauth2_service: BaseOAuth2Service

    def execute(self, strategy: DjangoStrategy, provider: str) -> str:
        self.provider_validator_service.validate(provider)

        backend = load_backend(
            strategy=strategy,
            name=self.oauth2_service.get_provider_by_name(provider),
            redirect_uri=self.oauth2_service.get_redirect_uri(provider),
        )

        return backend.auth_url()
