import pytest

from core.apps.channels.models import Channel
from core.apps.channels.use_cases.channels.delete_channel import DeleteChannelUseCase
from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser


@pytest.mark.django_db
def test_channel_and_user_deleted(delete_channel_use_case: DeleteChannelUseCase, channel: Channel):
    assert Channel.objects.filter(pk=channel.pk).exists()
    assert CustomUser.objects.filter(pk=channel.user_id).exists()

    delete_channel_use_case.execute(user=user_to_entity(channel.user))

    assert not Channel.objects.filter(pk=channel.pk).exists()
    assert not CustomUser.objects.filter(pk=channel.user_id).exists()
