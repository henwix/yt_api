import pytest

from core.apps.channels.models import Channel
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.models import VideoHistory
from core.apps.videos.use_cases.history.clear_history import ClearVideoHistoryUseCase
from core.tests.factories.videos import VideoHistoryModelFactory


@pytest.mark.parametrize('expected_history', [1, 5, 7, 13])
@pytest.mark.django_db
def test_history_cleared(
    clear_video_history_use_case: ClearVideoHistoryUseCase,
    channel: Channel,
    expected_history: int,
):
    VideoHistoryModelFactory.create_batch(size=expected_history, channel=channel)

    assert VideoHistory.objects.filter(channel=channel).count() == expected_history, 'not equal'

    response = clear_video_history_use_case.execute(user=user_to_entity(channel.user))

    assert response['status'] == 'history cleared'
    assert not VideoHistory.objects.filter(channel=channel).exists(), 'exists'


@pytest.mark.django_db
def test_history_empty(
    clear_video_history_use_case: ClearVideoHistoryUseCase,
    channel: Channel,
):
    assert not VideoHistory.objects.filter(channel=channel).exists()
    response = clear_video_history_use_case.execute(user=user_to_entity(channel.user))

    assert response['status'] == 'history is empty'
