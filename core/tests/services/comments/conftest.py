import punq
import pytest

from core.apps.videos.services.comments import BaseCommentService


@pytest.fixture
def comment_service(container: punq.Container) -> BaseCommentService:
    return container.resolve(BaseCommentService)
