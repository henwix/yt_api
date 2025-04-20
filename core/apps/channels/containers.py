import punq

from core.apps.channels.repositories.channels import (
    BaseChannelAboutRepository,
    BaseChannelAvatarRepository,
    BaseChannelMainRepository,
    BaseChannelRepository,
    BaseChannelSubsRepository,
    BaseSubscriptionRepository,
    ORMChannelAboutRepository,
    ORMChannelAvatarRepository,
    ORMChannelMainRepository,
    ORMChannelRepository,
    ORMChannelSubsRepository,
    ORMSubscriptionRepository,
)
from core.apps.channels.services.channels import (
    AvatarValidatorService,
    BaseAvatarValidatorService,
    BaseChannelAboutService,
    BaseChannelAvatarService,
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
    CeleryChannelAvatarService,
    ORMChannelAboutService,
    ORMChannelMainService,
    ORMChannelService,
    ORMChannelSubsService,
    ORMSubscriptionService,
)

from .providers.channels import (
    BaseChannelAvatarProvider,
    CeleryChannelProvider,
)


def init_channels(container: punq.Container) -> None:
    # repositories
    container.register(BaseChannelRepository, ORMChannelRepository)
    container.register(BaseChannelSubsRepository, ORMChannelSubsRepository)
    container.register(BaseChannelAvatarRepository, ORMChannelAvatarRepository)
    container.register(BaseChannelMainRepository, ORMChannelMainRepository)
    container.register(BaseChannelAboutRepository, ORMChannelAboutRepository)
    container.register(BaseSubscriptionRepository, ORMSubscriptionRepository)

    # services
    container.register(BaseAvatarValidatorService, AvatarValidatorService)
    container.register(BaseChannelService, ORMChannelService)
    container.register(BaseChannelSubsService, ORMChannelSubsService)
    container.register(BaseChannelAvatarService, CeleryChannelAvatarService)
    container.register(BaseChannelMainService, ORMChannelMainService)
    container.register(BaseChannelAboutService, ORMChannelAboutService)
    container.register(BaseSubscriptionService, ORMSubscriptionService)

    # providers
    container.register(BaseChannelAvatarProvider, CeleryChannelProvider)
