import punq

from core.apps.common.clients.email_client import EmailClient
from core.apps.users.providers.senders import (
    BaseSenderProvider,
    EmailSenderProvider,
)
from core.apps.users.repositories.users import (
    BaseUserRepository,
    ORMUserRepository,
)
from core.apps.users.services.codes import (
    BaseCodeService,
    EmailCodeService,
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


def init_users(container: punq.Container) -> None:
    #  services
    container.register(BaseUserService, ORMUserService)
    container.register(BaseUserValidatorService, UserExistsValidatorService)
    container.register(BaseCodeService, EmailCodeService)

    #  repositories
    container.register(BaseUserRepository, ORMUserRepository)

    #  senders
    container.register(BaseSenderProvider, EmailSenderProvider)

    #  use cases
    container.register(AuthorizeUserUseCase)
    container.register(VerifyCodeUseCase)

    #  clients
    container.register(EmailClient)
