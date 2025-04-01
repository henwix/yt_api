import pytest
from apps.channels.exceptions.channels import ChannelNotFoundError
from apps.channels.models import Channel
from apps.channels.services.channels import BaseChannelService
from django.contrib.auth.models import User
from faker import Faker
from rest_framework.test import APIClient

from tests.factories.channels import UserModelFactory

fake = Faker()


@pytest.mark.django_db
def test_channel_not_exists(channel_service: BaseChannelService):
    """Test get_channel when user's channel does not exists in database"""
    with pytest.raises(ChannelNotFoundError):
        user = UserModelFactory()
        channel_service.get_channel(user)


@pytest.mark.django_db
def test_channel_exists(channel_service: BaseChannelService, user_with_channel: User):
    """Test get_channel when a user has an existing channel in database"""
    assert user_with_channel.channel == channel_service.get_channel(user_with_channel)


@pytest.mark.django_db
def test_channel_and_user_delete(channel_service: BaseChannelService, user_with_channel: User):
    """Test deleting a user and their channel from database"""
    channel_service.delete_channel(user_with_channel)

    assert not Channel.objects.filter(user_id=user_with_channel.pk).exists()
    assert not User.objects.filter(id=user_with_channel.pk).exists()


@pytest.mark.django_db
def test_channel_patch_data(client: APIClient, jwt_access: str):
    """Test GET request to retrieve channel's data. Status code should be 200"""
    client.credentials(HTTP_AUTHORIZATION=jwt_access)
    response = client.get('/api/v1/channel/')

    assert response.status_code == 200
