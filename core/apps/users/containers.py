import punq

from core.apps.common.clients.email_client import EmailClient
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
    BaseOAuth2ProviderValidatorService,
    BaseOAuth2Service,
    OAuth2ProviderValidatorService,
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
from core.apps.users.use_cases.oauth2_connect import OAuth2ConnectUseCase
from core.apps.users.use_cases.oauth2_connected_providers import OAuth2ConnectedProvidersUseCase
from core.apps.users.use_cases.oauth2_disconnect import OAuth2DisconnectUseCase
from core.apps.users.use_cases.oauth2_generate_url import OAuth2GenerateURLUseCase
from core.apps.users.use_cases.user_create import UserCreateUseCase
from core.apps.users.use_cases.user_reset_password import UserResetPasswordUseCase
from core.apps.users.use_cases.user_reset_password_confirm import UserResetPasswordConfirmUseCase
from core.apps.users.use_cases.user_reset_username import UserResetUsernameUseCase
from core.apps.users.use_cases.user_reset_username_confirm import UserResetUsernameConfirmUseCase
from core.apps.users.use_cases.user_set_email import UserSetEmailUseCase
from core.apps.users.use_cases.user_set_email_confirm import UserSetEmailConfirmUseCase
from core.apps.users.use_cases.user_set_password import UserSetPasswordUseCase


def init_users(container: punq.Container) -> None:
    #  services
    container.register(BaseUserService, ORMUserService)
    container.register(BaseUserValidatorService, UserExistsValidatorService)
    container.register(BaseCodeService, EmailCodeService)
    container.register(BaseOAuth2Service, OAuth2Service)
    container.register(BaseOAuth2ProviderValidatorService, OAuth2ProviderValidatorService)

    #  repositories
    container.register(BaseUserRepository, ORMUserRepository)
    container.register(BaseOAuth2Repository, OAuth2Repository)

    #  use cases
    container.register(AuthorizeUserUseCase)
    container.register(VerifyCodeUseCase)

    container.register(UserCreateUseCase)
    container.register(UserSetPasswordUseCase)
    container.register(UserSetEmailUseCase)
    container.register(UserSetEmailConfirmUseCase)
    container.register(UserResetPasswordUseCase)
    container.register(UserResetPasswordConfirmUseCase)
    container.register(UserResetUsernameUseCase)
    container.register(UserResetUsernameConfirmUseCase)

    container.register(OAuth2GenerateURLUseCase)
    container.register(OAuth2ConnectUseCase)
    container.register(OAuth2DisconnectUseCase)
    container.register(OAuth2ConnectedProvidersUseCase)

    #  clients
    container.register(EmailClient)
