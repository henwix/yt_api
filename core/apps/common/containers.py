import punq

from core.apps.common.services.boto_client import (
    BaseBotoClientService,
    BotoClientService,
)
from core.apps.common.services.cache import (
    BaseCacheService,
    CacheService,
)


def initialize_common(container: punq.Container):
    container.register(BaseCacheService, CacheService)
    container.register(BaseBotoClientService, BotoClientService)
