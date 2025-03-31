import pytest
from apps.channels.services.channels import BaseChannelMainService
from project.containers import get_container


@pytest.fixture
def main_channel_service() -> BaseChannelMainService:
    container = get_container()
    return container.resolve(BaseChannelMainService)
