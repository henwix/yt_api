import pytest
from django.db.models import Sum
from rest_framework.test import APIClient

from core.apps.channels.models import Channel
from core.apps.videos.models import Video


@pytest.mark.django_db
def test_channel_patch_data(client: APIClient, jwt_access: str):
    """Test GET request to retrieve channel's data. Status code should be 200"""
    client.credentials(HTTP_AUTHORIZATION=jwt_access)
    response = client.get('/api/v1/channel/')

    assert response.status_code == 200


@pytest.mark.skip('not completed')
def test_channel_about_correct(client: APIClient, channel: Channel):
    # expected_link = f'http://127.0.0.1:8001/api/v1/c/{channel.slug}'
    expected_views = Video.objects.filter(author=channel).aggregate(v=Sum('views'))['v']

    response = client.get(f'/api/v1/c/{channel.slug}/about')

    assert response.status_code == 200
    assert response.data.get('description') == channel.description
    # assert response.data.get('date_joined') == channel.user.date_joined
    assert response.data.get('country') == channel.country
    # assert response.data.get('channel_link') == expected_link
    assert response.data.get('total_views') == expected_views
    assert response.data.get('total_videos') == channel.videos.count()
    assert response.data.get('total_subs') == channel.followers.count()
