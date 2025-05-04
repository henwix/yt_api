import punq

from core.apps.common.adapters.boto_file_provider import BotoFileProvider
from core.apps.common.adapters.celery_file_provider import CeleryFileProvider
from core.apps.common.clients.boto_client import BotoClient
from core.apps.common.clients.email_client import EmailClient
from core.apps.common.providers.files import (
    BaseBotoFileProvider,
    BaseCeleryFileProvider,
)
from core.apps.common.services.cache import (
    BaseCacheService,
    CacheService,
)
from core.apps.common.services.files import (
    BaseS3FileService,
    S3FileService,
)


def init_common(container: punq.Container):
    # services
    container.register(BaseCacheService, CacheService)
    container.register(BaseS3FileService, S3FileService)

    # clients
    container.register(BotoClient)
    container.register(EmailClient)

    # providers
    container.register(BaseBotoFileProvider, BotoFileProvider)
    container.register(BaseCeleryFileProvider, CeleryFileProvider)
