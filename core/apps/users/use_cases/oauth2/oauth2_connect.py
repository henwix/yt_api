from dataclasses import dataclass

from social_core.backends.oauth import BaseOAuth2
from social_django.strategy import DjangoStrategy
from social_django.utils import load_backend

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser
from core.apps.users.services.oauth2 import (
    BaseOAuth2ProviderValidatorService,
    BaseOAuth2Service,
)
from core.apps.users.services.users import BaseUserService


@dataclass
class OAuth2ConnectUseCase:
    """Use case for OAuth2 connection.

    If the user is authenticated, it returns a message that the chosen
    provider is connected.

    If the user is anonymous, it creates a channel and returns JWT
    tokens

    """

    user_service: BaseUserService
    channel_service: BaseChannelService
    provider_validator_service: BaseOAuth2ProviderValidatorService
    oauth2_service: BaseOAuth2Service

    def execute(self, strategy: DjangoStrategy, user: CustomUser, provider: str) -> dict:
        # Validate provider
        self.provider_validator_service.validate(provider)

        # Load OAuth2 backend
        backend: BaseOAuth2 = load_backend(
            strategy=strategy,
            name=self.oauth2_service.get_provider_by_name(provider),
            redirect_uri=self.oauth2_service.get_redirect_uri(provider),
        )

        # Complete Social OAuth and retrieve or create user
        retrieved_user = user_to_entity(
            backend.auth_complete(user=user if user.is_authenticated else None),
        )

        if not user.is_authenticated:
            channel = self.channel_service.get_channel_by_user_or_none(
                user=retrieved_user,
            )
            if not channel:
                self.channel_service.create_channel_by_user_info(user=retrieved_user)

            return self.user_service.generate_jwt(user=retrieved_user)

        return {'detail': f'{provider} successfully connected'}
