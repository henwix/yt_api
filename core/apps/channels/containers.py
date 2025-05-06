import punq

from core.apps.channels.repositories.channels import (
    BaseChannelAboutRepository,
    BaseChannelMainRepository,
    BaseChannelRepository,
    BaseChannelSubsRepository,
    BaseSubscriptionRepository,
    ORMChannelAboutRepository,
    ORMChannelMainRepository,
    ORMChannelRepository,
    ORMChannelSubsRepository,
    ORMSubscriptionRepository,
)
from core.apps.channels.services.channels import (
    BaseChannelAboutService,
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
    ORMChannelAboutService,
    ORMChannelMainService,
    ORMChannelService,
    ORMChannelSubsService,
    ORMSubscriptionService,
)
from core.apps.channels.services.s3_channels import (
    AvatarExistsValidatorService,
    AvatarFilenameExistsValidatorService,
    AvatarFilenameFormatValidatorService,
    BaseAvatarFilenameValidatorService,
    BaseAvatarValidatorService,
    ComposedAvatarFilenameValidatorService,
)
from core.apps.channels.use_cases.avatar_upload.complete_upload_avatar import CompleteUploadAvatarUseCase
from core.apps.channels.use_cases.avatar_upload.delete_avatar import DeleteChannelAvatarUseCase
from core.apps.channels.use_cases.avatar_upload.download_avatar_url import GenerateUrlForAvatarDownloadUseCase
from core.apps.channels.use_cases.avatar_upload.upload_avatar_url import GenerateUploadAvatarUrlUseCase


def init_channels(container: punq.Container) -> None:
    def build_avatar_filename_validators() -> BaseAvatarFilenameValidatorService:
        return ComposedAvatarFilenameValidatorService(
            validators=[
                container.resolve(AvatarFilenameExistsValidatorService),
                container.resolve(AvatarFilenameFormatValidatorService),
            ],
        )

    # repositories
    container.register(BaseChannelRepository, ORMChannelRepository)
    container.register(BaseChannelSubsRepository, ORMChannelSubsRepository)
    container.register(BaseChannelMainRepository, ORMChannelMainRepository)
    container.register(BaseChannelAboutRepository, ORMChannelAboutRepository)
    container.register(BaseSubscriptionRepository, ORMSubscriptionRepository)

    # services
    container.register(BaseChannelService, ORMChannelService)
    container.register(BaseChannelSubsService, ORMChannelSubsService)
    container.register(BaseChannelMainService, ORMChannelMainService)
    container.register(BaseChannelAboutService, ORMChannelAboutService)

    container.register(BaseSubscriptionService, ORMSubscriptionService)

    # validator services
    container.register(BaseAvatarValidatorService, AvatarExistsValidatorService)
    container.register(AvatarFilenameExistsValidatorService)
    container.register(AvatarFilenameFormatValidatorService)
    container.register(BaseAvatarFilenameValidatorService, factory=build_avatar_filename_validators)

    # use cases
    container.register(GenerateUploadAvatarUrlUseCase)
    container.register(DeleteChannelAvatarUseCase)
    container.register(GenerateUrlForAvatarDownloadUseCase)
    container.register(CompleteUploadAvatarUseCase)
