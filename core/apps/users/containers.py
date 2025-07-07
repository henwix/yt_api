import punq

from core.apps.common.clients.email_client import EmailClient
from core.apps.users.providers.senders import (
    BaseSenderProvider,
    EmailSenderProvider,
)
from core.apps.users.repositories.oauth2 import (
    BaseOAuth2Repository,
    OAuth2Repository,
)
from core.apps.users.repositories.users import (
    BaseUserRepository,
    ORMUserRepository,
)
from core.apps.users.services.codes import (
    BaseCodeService,
    EmailCodeService,
)
from core.apps.users.services.oauth2 import (
    BaseOAuth2Service,
    OAuth2Service,
)
from core.apps.users.services.users import (
    BaseUserService,
    BaseUserValidatorService,
    ORMUserService,
    UserExistsValidatorService,
)
from core.apps.users.use_cases.auth import (
    AuthorizeUserUseCase,
    VerifyCodeUseCase,
)
from core.apps.users.use_cases.oauth2_complete import OAuth2CompleteUseCase
from core.apps.users.use_cases.oauth2_connected_providers import OAuth2ConnectedProvidersUseCase


def init_users(container: punq.Container) -> None:
    #  services
    container.register(BaseUserService, ORMUserService)
    container.register(BaseUserValidatorService, UserExistsValidatorService)
    container.register(BaseCodeService, EmailCodeService)
    container.register(BaseOAuth2Service, OAuth2Service)

    #  repositories
    container.register(BaseUserRepository, ORMUserRepository)
    container.register(BaseOAuth2Repository, OAuth2Repository)

    #  senders
    container.register(BaseSenderProvider, EmailSenderProvider)

    #  use cases
    container.register(AuthorizeUserUseCase)
    container.register(VerifyCodeUseCase)

    container.register(OAuth2CompleteUseCase)
    container.register(OAuth2ConnectedProvidersUseCase)

    #  clients
    container.register(EmailClient)
