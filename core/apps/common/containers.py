import punq

from core.apps.common.clients.email_client import EmailClient
from core.apps.common.services.boto_client import (
    BaseBotoClientService,
    BotoClientService,
)
from core.apps.common.services.cache import (
    BaseCacheService,
    CacheService,
)


def init_common(container: punq.Container):
    container.register(BaseCacheService, CacheService)
    container.register(BaseBotoClientService, BotoClientService)

    container.register(EmailClient)
