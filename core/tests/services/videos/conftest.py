import punq
import pytest

from core.apps.videos.services.s3_videos import BaseVideoFilenameValidatorService
from core.apps.videos.services.videos import (
    BasePrivateVideoPermissionValidatorService,
    BaseVideoService,
)


@pytest.fixture
def video_service(container: punq.Container) -> BaseVideoService:
    return container.resolve(BaseVideoService)


@pytest.fixture
def video_permission_validator_service(container: punq.Container) -> BasePrivateVideoPermissionValidatorService:
    return container.resolve(BasePrivateVideoPermissionValidatorService)


@pytest.fixture
def video_filename_validator_service(container: punq.Container) -> BaseVideoFilenameValidatorService:
    return container.resolve(BaseVideoFilenameValidatorService)
