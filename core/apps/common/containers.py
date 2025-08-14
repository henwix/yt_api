import punq

from core.apps.common.adapters.boto_file_provider import BotoFileProvider
from core.apps.common.adapters.celery_file_provider import CeleryFileProvider
from core.apps.common.clients.boto_client import BotoClient
from core.apps.common.clients.email_client import EmailClient
from core.apps.common.providers.cache import (
    BaseCacheProvider,
    RedisCacheProvider,
)
from core.apps.common.providers.captcha import (
    BaseCaptchaProvider,
    GoogleCaptchaProvider,
)
from core.apps.common.providers.files import (
    BaseBotoFileProvider,
    BaseCeleryFileProvider,
)
from core.apps.common.services.cache import (
    BaseCacheService,
    CacheService,
)
from core.apps.common.services.captcha import (
    BaseCaptchaService,
    GoogleV3CaptchaService,
)
from core.apps.common.services.files import (
    BaseFileExistsInS3ValidatorService,
    BaseMultipartUploadExistsInS3ValidatorService,
    BaseS3FileService,
    FileExistsInS3ValidatorService,
    MultipartUploadExistsInS3ValidatorService,
    S3FileService,
)


def init_common(container: punq.Container):
    # providers
    container.register(BaseCacheProvider, RedisCacheProvider)
    container.register(BaseBotoFileProvider, BotoFileProvider)
    container.register(BaseCeleryFileProvider, CeleryFileProvider)
    container.register(BaseCaptchaProvider, GoogleCaptchaProvider)

    # services
    container.register(BaseCacheService, CacheService)
    container.register(BaseS3FileService, S3FileService)
    container.register(BaseFileExistsInS3ValidatorService, FileExistsInS3ValidatorService)
    container.register(BaseMultipartUploadExistsInS3ValidatorService, MultipartUploadExistsInS3ValidatorService)
    container.register(BaseCaptchaService, GoogleV3CaptchaService)

    # clients
    container.register(BotoClient)
    container.register(EmailClient)
