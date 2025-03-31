import punq

from apps.channels.repositories.channels import (
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
from apps.channels.services.channels import (
    AvatarValidatorService,
    BaseAvatarValidatorService,
    BaseChannelAboutService,
    BaseChannelAvatarService,
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
    CeleryChannelAvatarService,
    ChannelAboutService,
    ChannelMainService,
    ChannelSubsService,
    ORMChannelService,
    SubscriptionService,
)

from .providers.channels import BaseChannelAvatarProvider, CeleryChannelProvider


def initialize_channels(container: punq.Container) -> None:
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
    container.register(BaseChannelSubsService, ChannelSubsService)
    container.register(BaseChannelAvatarService, CeleryChannelAvatarService)
    container.register(BaseChannelMainService, ChannelMainService)
    container.register(BaseChannelAboutService, ChannelAboutService)
    container.register(BaseSubscriptionService, SubscriptionService)

    # providers
    container.register(BaseChannelAvatarProvider, CeleryChannelProvider)
