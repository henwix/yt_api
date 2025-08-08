from django.core.cache import cache
from rest_framework.test import APIClient

import pytest

from core.apps.channels.models import Channel
from core.tests.factories.channels import SubscriptionItemModelFactory
from core.tests.factories.videos import (
    VideoModelFactory,
    VideoViewModelFactory,
)


@pytest.mark.django_db
def test_channel_data_retrieved_correctly(client: APIClient, jwt_and_channel):
    """Test that channel data was retrieved after GET request to the endpoint: /v1/channel/"""

    cache.delete('retrieve_channel_1')  # delete cache with user_id 1

    jwt, channel = jwt_and_channel
    client.credentials(HTTP_AUTHORIZATION=jwt)

    response = client.get('/v1/channel/')

    assert response.status_code == 200, 'incorrect code'
    assert response.data.get('name') == channel.name, 'incorrect name'
    assert response.data.get('slug') == channel.slug, 'incorrect slug'
    assert response.data.get('description') == channel.description, 'incorrect desc'
    assert response.data.get('country') == channel.country, 'incorrect country'


@pytest.mark.django_db
def test_channel_data_changed_correctly(client: APIClient, jwt: str):
    """Test that channel data was changed after PATCH request to the endpoint: /v1/channel/."""

    url = '/v1/channel/'
    payload = {
        'name': 'TestName123',
        'slug': 'TestSlug123',
        'description': 'Test description 123',
        'country': 'TestCountry123',
    }
    client.credentials(HTTP_AUTHORIZATION=jwt)

    client.patch(url, payload)
    response = client.get(url)

    assert response.status_code == 200, 'incorrect code'
    assert payload.get('name') == response.data.get('name'), 'incorrect name'
    assert payload.get('slug') == response.data.get('slug'), 'incorrect slug'
    assert payload.get('description') == response.data.get('description'), 'incorrect description'
    assert payload.get('country') == response.data.get('country'), 'incorrect country'


@pytest.mark.django_db
@pytest.mark.parametrize('expected_videos, expected_views, expected_subs', ([3, 10, 5], [5, 2, 1], [8, 4, 10]))
def test_channel_about_data_retrieved_correctly(
    client: APIClient, channel: Channel, expected_videos, expected_views, expected_subs,
):
    """Test that channel's about data was retrieved after GET request to the
    endpoint: channel's about page."""

    v = VideoModelFactory.create_batch(size=expected_videos, author=channel)  # create videos
    VideoViewModelFactory.create_batch(size=expected_views, video=v[0])  # create views
    SubscriptionItemModelFactory.create_batch(size=expected_subs, subscribed_to=channel)  # create subs

    response = client.get(f'/v1/channels/{channel.slug}/about')

    assert response.status_code == 200, 'incorrect code'
    assert response.data.get('description') == channel.description, 'incorrect desc'
    assert response.data.get('country') == channel.country, 'incorrect country'
    assert response.data.get('total_views') == expected_views, 'incorrect views'
    assert response.data.get('total_videos') == channel.videos.count(), 'incorrect videos'
    assert response.data.get('total_subs') == channel.followers.count(), 'incorrect subs'
