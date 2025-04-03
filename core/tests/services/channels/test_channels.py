import random

import pytest
from django.contrib.auth.models import User
from faker import Faker

from core.apps.channels.exceptions.channels import ChannelNotFoundError, SelfSubscriptionError, SubscriptionExistsError
from core.apps.channels.models import Channel
from core.apps.channels.services.channels import BaseChannelService, BaseChannelSubsService, BaseSubscriptionService
from core.tests.factories.channels import SubscriptionItemModelFactory, UserModelFactory

fake = Faker()


@pytest.mark.django_db
def test_channel_not_exists_error(channel_service: BaseChannelService):
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
def test_subscribers_list_empty(channel_sub_service: BaseChannelSubsService, channel: Channel):
    """Test subscriptions count zero with no subscribers in database"""
    subs = channel_sub_service.get_subscriber_list(channel=channel)
    assert subs.count() == 0


@pytest.mark.django_db
def test_subscribers_exists(channel_sub_service: BaseChannelSubsService, channel: Channel):
    """Test channel's subscribers retrieved from database"""
    expected_value = random.randint(1, 15)

    SubscriptionItemModelFactory.create_batch(size=expected_value, subscribed_to=channel)
    subs = channel_sub_service.get_subscriber_list(channel=channel)

    assert subs.count() == expected_value


@pytest.mark.django_db
def test_subscribe_exists_error(subscription_service: BaseSubscriptionService):
    """Test subscription to channel already exists"""
    with pytest.raises(SubscriptionExistsError):
        subscription = SubscriptionItemModelFactory()

        subscription_service.subscribe(user=subscription.subscriber.user, channel_slug=subscription.subscribed_to.slug)


@pytest.mark.django_db
def test_subscribe_to_yourself_error(subscription_service: BaseSubscriptionService, channel: Channel):
    """Test if the channels are the same when subscribing"""
    with pytest.raises(SelfSubscriptionError):
        subscription_service.subscribe(user=channel.user, channel_slug=channel.slug)


@pytest.mark.django_db
def test_unsubscribe_from_yourself_error(subscription_service: BaseSubscriptionService, channel: Channel):
    """Test if the channels are the same when unsubscribing"""
    with pytest.raises(SelfSubscriptionError):
        subscription_service.unsubscribe(user=channel.user, channel_slug=channel.slug)
