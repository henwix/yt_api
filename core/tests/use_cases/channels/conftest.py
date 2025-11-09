import punq
import pytest

from core.apps.channels.use_cases.channels.delete_channel import DeleteChannelUseCase


@pytest.fixture
def delete_channel_use_case(container: punq.Container) -> DeleteChannelUseCase:
    return container.resolve(DeleteChannelUseCase)
