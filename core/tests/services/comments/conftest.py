import punq
import pytest

from core.apps.videos.models import (
    VideoComment,
    VideoCommentLikeItem,
)
from core.apps.videos.services.comments import BaseVideoCommentService
from core.tests.factories.video_comments import (
    VideoCommentLikeFactoryItem,
    VideoCommentModelFactory,
)


@pytest.fixture
def comment_service(container: punq.Container) -> BaseVideoCommentService:
    return container.resolve(BaseVideoCommentService)


@pytest.fixture
def comment() -> VideoComment:
    return VideoCommentModelFactory()


@pytest.fixture
def like() -> VideoCommentLikeItem:
    return VideoCommentLikeFactoryItem()
