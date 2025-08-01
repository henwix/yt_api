import punq
import pytest

from core.apps.videos.use_cases.history.clear_history import ClearVideoHistoryUseCase


@pytest.fixture
def clear_video_history_use_case(container: punq.Container) -> ClearVideoHistoryUseCase:
    return container.resolve(ClearVideoHistoryUseCase)
