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
from apps.channels.serializers import ChannelSerializer
from apps.channels.services.channels import (
    BaseChannelAboutService,
    BaseChannelAvatarService,
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
    CachedORMChannelService,
    ChannelAboutService,
    ChannelAvatarService,
    ChannelMainService,
    ChannelSubsService,
    SubscriptionService,
)


def initialize_channels(container: punq.Container) -> None:
    # repositories
    container.register(BaseChannelRepository, ORMChannelRepository)
    container.register(BaseChannelSubsRepository, ORMChannelSubsRepository)
    container.register(BaseChannelAvatarRepository, ORMChannelAvatarRepository)
    container.register(BaseChannelMainRepository, ORMChannelMainRepository)
    container.register(BaseChannelAboutRepository, ORMChannelAboutRepository)
    container.register(BaseSubscriptionRepository, ORMSubscriptionRepository)

    # services
    container.register(BaseChannelService, CachedORMChannelService, serializer_class=ChannelSerializer)
    container.register(BaseChannelSubsService, ChannelSubsService)
    container.register(BaseChannelAvatarService, ChannelAvatarService)
    container.register(BaseChannelMainService, ChannelMainService)
    container.register(BaseChannelAboutService, ChannelAboutService)
    container.register(BaseSubscriptionService, SubscriptionService)
