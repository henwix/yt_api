import punq

from core.apps.users.providers.senders import (
    BaseSenderProvider,
    EmailSenderProvider,
)
from core.apps.users.repositories.users import (
    BaseUserRepository,
    UserRepository,
)
from core.apps.users.services.codes import (
    BaseCodeService,
    EmailCodeService,
)
from core.apps.users.services.users import (
    BaseUserService,
    BaseUserValidatorService,
    UserService,
    UserValidatorService,
)
from core.apps.users.use_cases.auth import (
    AuthorizeUserUseCase,
    VerifyCodeUseCase,
)


def init_users(container: punq.Container) -> None:
    #  services
    container.register(BaseUserService, UserService)
    container.register(BaseUserValidatorService, UserValidatorService)
    container.register(BaseCodeService, EmailCodeService)

    #  repositories
    container.register(BaseUserRepository, UserRepository)

    #  senders
    container.register(BaseSenderProvider, EmailSenderProvider)

    #  use cases
    container.register(AuthorizeUserUseCase)
    container.register(VerifyCodeUseCase)
