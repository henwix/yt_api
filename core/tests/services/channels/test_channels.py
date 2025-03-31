import pytest
from apps.channels.services.channels import BaseChannelMainService


@pytest.mark.django_db
def test_main_channel(main_channel_service: BaseChannelMainService):
    assert True
