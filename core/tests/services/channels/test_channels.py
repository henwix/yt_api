from django.contrib.auth import get_user_model
from django.utils.text import slugify

import pytest

from core.apps.channels.converters.channels import (
    channel_from_entity,
    channel_to_entity,
)
from core.apps.channels.entities.channels import ChannelEntity
from core.apps.channels.exceptions.channels import (
    ChannelNotFoundError,
    ChannelSlugInvalidValueError,
)
from core.apps.channels.exceptions.subscriptions import (
    SelfSubscriptionError,
    SubscriptionDoesNotExistsError,
    SubscriptionExistsError,
)
from core.apps.channels.models import (
    Channel,
    SubscriptionItem,
)
from core.apps.channels.services.channels import (
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
)
from core.apps.users.converters.users import user_to_entity
from core.apps.users.exceptions.users import UserWithThisDataAlreadyExistsError
from core.apps.users.models import CustomUser
from core.tests.factories.channels import (
    ChannelModelFactory,
    SubscriptionItemModelFactory,
    UserModelFactory,
)
from core.tests.factories.videos import VideoModelFactory


User = get_user_model()


@pytest.mark.django_db
def test_channel_not_found_error(channel_service: BaseChannelService):
    """Test get_channel when user's channel does not exists in database."""

    with pytest.raises(ChannelNotFoundError):
        user = UserModelFactory()
        channel_service.get_channel_by_user_or_404(user)


@pytest.mark.django_db
def test_channel_retrieved_from_channel_or_404(channel_service: BaseChannelService, user_with_channel: User):
    """Test get_channel when a user has an existing channel in database."""

    channel_dto = channel_from_entity(
        channel=channel_service.get_channel_by_user_or_404(
            user=user_to_entity(user_with_channel),
        ),
    )
    assert user_with_channel.channel == channel_dto


@pytest.mark.django_db
def test_channel_is_none(channel_service: BaseChannelService):
    """Test get_channel when a user does not have a channel in database."""

    assert channel_service.get_channel_by_user_or_none(UserModelFactory()) is None


@pytest.mark.django_db
def test_channel_retrieved_from_channel_or_none(channel_service: BaseChannelService, user_with_channel: User):
    """Test get_channel when a user has an existing channel in database."""

    channel_dto = channel_from_entity(
        channel=channel_service.get_channel_by_user_or_none(
            user=user_to_entity(user_with_channel),
        ),
    )
    assert user_with_channel.channel == channel_dto


@pytest.mark.django_db
def test_channel_and_user_delete(channel_service: BaseChannelService, user_with_channel: User):
    """Test deleting a user and their channel from database."""

    channel_service.delete_channel(
        user=user_to_entity(user_with_channel),
    )

    assert not Channel.objects.filter(user_id=user_with_channel.pk).exists()
    assert not User.objects.filter(id=user_with_channel.pk).exists()


@pytest.mark.django_db
def test_subscribers_list_empty(channel_sub_service: BaseChannelSubsService, channel: Channel):
    """Test subscriptions count zero with no subscribers in database."""

    subs = channel_sub_service.get_subscriber_list(channel=channel_to_entity(channel))
    assert subs.count() == 0


@pytest.mark.django_db
def test_subscribers_exists(channel_sub_service: BaseChannelSubsService, channel: Channel):
    """Test channel's subscribers retrieved from database."""

    expected_value = 10

    SubscriptionItemModelFactory.create_batch(size=expected_value, subscribed_to=channel)
    subs = channel_sub_service.get_subscriber_list(channel=channel_to_entity(channel))

    assert subs.count() == expected_value


@pytest.mark.django_db
def test_subscribe_exists_error(subscription_service: BaseSubscriptionService):
    """Test subscription to channel already exists."""

    with pytest.raises(SubscriptionExistsError):
        subscription = SubscriptionItemModelFactory()
        subscription_service.subscribe(
            user=user_to_entity(subscription.subscriber.user),
            channel_slug=subscription.subscribed_to.slug,
        )


@pytest.mark.django_db
def test_subscribe_does_not_exists_error(subscription_service: BaseSubscriptionService):
    """Test subscription to channel does not exists in database."""

    with pytest.raises(SubscriptionDoesNotExistsError):
        subscriber, subscribed_to = ChannelModelFactory.create_batch(size=2)
        subscription_service.unsubscribe(user=user_to_entity(subscriber.user), channel_slug=subscribed_to.slug)


@pytest.mark.django_db
def test_subscribe_to_yourself_error(subscription_service: BaseSubscriptionService, channel: Channel):
    """Test if the channels are the same when subscribing."""

    with pytest.raises(SelfSubscriptionError):
        subscription_service.subscribe(user=user_to_entity(channel.user), channel_slug=channel.slug)


@pytest.mark.django_db
def test_unsubscribe_from_yourself_error(subscription_service: BaseSubscriptionService, channel: Channel):
    """Test if the channels are the same when unsubscribing."""

    with pytest.raises(SelfSubscriptionError):
        subscription_service.unsubscribe(user=user_to_entity(channel.user), channel_slug=channel.slug)


@pytest.mark.django_db
def test_subscription_created(subscription_service: BaseSubscriptionService):
    """Test created subscription to channel exists in database."""

    subscriber, subscribed_to = ChannelModelFactory.create_batch(size=2)

    assert not SubscriptionItem.objects.filter(subscriber=subscriber, subscribed_to=subscribed_to).exists()

    subscription_service.subscribe(user=user_to_entity(subscriber.user), channel_slug=subscribed_to.slug)
    assert SubscriptionItem.objects.filter(subscriber=subscriber, subscribed_to=subscribed_to).exists()


@pytest.mark.django_db
def test_subscription_deleted(subscription_service: BaseSubscriptionService):
    """Test deleted subscription to channel not in database."""

    subscriber, subscribed_to = ChannelModelFactory.create_batch(size=2)

    subscription_service.subscribe(user=user_to_entity(subscriber.user), channel_slug=subscribed_to.slug)
    assert SubscriptionItem.objects.filter(subscriber=subscriber, subscribed_to=subscribed_to).exists()

    subscription_service.unsubscribe(user=user_to_entity(subscriber.user), channel_slug=subscribed_to.slug)
    assert not SubscriptionItem.objects.filter(subscriber=subscriber, subscribed_to=subscribed_to).exists()


@pytest.mark.django_db
def test_main_channel_page_correct(channel_main_service: BaseChannelMainService, channel: Channel):
    """Test main channel page data retrieved correctly."""

    expected_subs = 10
    expected_videos = 5  # not more than 5 because main_channel endpoint returns last 5 videos

    SubscriptionItemModelFactory.create_batch(size=expected_subs, subscribed_to=channel)
    VideoModelFactory.create_batch(size=expected_videos, author=channel)

    response = channel_main_service.get_channel_main_page_list().filter(slug=channel.slug).first()

    assert response is not None
    assert response.slug == channel.slug
    assert response.name == channel.name
    assert response.description == channel.description
    assert response.subs_count == expected_subs
    assert response.videos.count() == expected_videos
    assert response.subs_count == expected_subs
    assert response.videos.count() == expected_videos


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_channel_name, expected_channel_slug, expected_channel_description, expected_channel_country',
    argvalues=(
        ['Channel Test Name', 'test_channel_slug', 'Test Channel description', 'US'],
        ['Channel123.Name1235', 'test_channel_slug-123', 'Testchanneldescription', 'United States'],
        ['channel_test_n@mete$t', 'channel_slug_123-123', 'description', 'Test Country'],
        ['this is my a test channel name', 'd-aghsldgf1akslnf1-sad', 'FN(*LASJKFHn', 'Channel Country Test'],
    ),
)
def test_channel_created_by_provided_data(
    channel_service: BaseChannelService,
    user: CustomUser,
    expected_channel_name: str,
    expected_channel_slug: str,
    expected_channel_description: str,
    expected_channel_country: str,
):
    """Test that the channel has been created by provided data."""

    created_object: ChannelEntity = channel_service.create_by_data(
        data={
            'channel': {
                'user': user,
                'name': expected_channel_name,
                'slug': expected_channel_slug,
                'description': expected_channel_description,
                'country': expected_channel_country,
            },
        },
    )

    database_object = Channel.objects.get(user=user)

    assert isinstance(created_object, ChannelEntity)

    assert created_object.name == expected_channel_name
    assert database_object.name == expected_channel_name

    assert created_object.slug == expected_channel_slug
    assert database_object.slug == expected_channel_slug

    assert created_object.description == expected_channel_description
    assert database_object.description == expected_channel_description

    assert created_object.country == expected_channel_country
    assert database_object.country == expected_channel_country

    assert created_object.avatar_s3_key is None
    assert database_object.avatar_s3_key is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_username',
    argvalues=['test_username', 'my_TestUsername', 'hello_world', 'tHiS_is_mY_a_teSt_username'],
)
def test_channel_created_based_on_user_username(
    channel_service: BaseChannelService,
    expected_username: str,
):
    """Test that the channel has been created based on user's username."""

    user = UserModelFactory.create(username=expected_username)

    created_object: ChannelEntity = channel_service.create_by_data(
        data={
            'username': expected_username,
            'channel': {
                'user': user,
            },
        },
    )

    database_object = Channel.objects.get(user=user)

    assert isinstance(created_object, ChannelEntity)

    assert created_object.name == expected_username
    assert database_object.name == expected_username

    assert created_object.slug == slugify(expected_username)
    assert database_object.slug == slugify(expected_username)

    assert created_object.description is None
    assert database_object.description is None

    assert created_object.country is None
    assert database_object.country is None

    assert created_object.avatar_s3_key is None
    assert database_object.avatar_s3_key is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_channel_name',
    argvalues=[
        'Test.Channel Name',
        'test_channel_name',
        'channel_123_4556_name-123kmasnbf',
        'tHiS._is_mY_teSt_channel Name',
    ],
)
def test_channel_created_based_on_channel_name(
    channel_service: BaseChannelService,
    expected_channel_name: str,
):
    """Test that the channel has been created with slug based on channel's
    name."""

    user = UserModelFactory.create()

    created_object: ChannelEntity = channel_service.create_by_data(
        data={
            'channel': {
                'user': user,
                'name': expected_channel_name,
            },
        },
    )

    database_object = Channel.objects.get(user=user)

    assert isinstance(created_object, ChannelEntity)

    assert created_object.name == expected_channel_name
    assert database_object.name == expected_channel_name

    assert created_object.slug == slugify(expected_channel_name)
    assert database_object.slug == slugify(expected_channel_name)

    assert created_object.description is None
    assert database_object.description is None

    assert created_object.country is None
    assert database_object.country is None

    assert created_object.avatar_s3_key is None
    assert database_object.avatar_s3_key is None


@pytest.mark.django_db
def test_channel_slug_exists_error(
    channel_service: BaseChannelService,
):
    """Test that an error has been raised when the channel with this slug
    already exists."""

    expected_channel_slug = 'test_channel_slug'

    ChannelModelFactory.create(slug=expected_channel_slug)

    with pytest.raises(UserWithThisDataAlreadyExistsError):
        channel_service.create_by_data(
            data={
                'channel': {
                    'name': 'test_channel_name',
                    'slug': expected_channel_slug,
                },
            },
        )


@pytest.mark.django_db
@pytest.mark.parametrize('expected_channel_slug', ['HelloWorldSlug', 'test_slug.test', 'TeSt.SlUg_123', '123.123ABC'])
def test_channel_slug_invalid_value_error(
    channel_service: BaseChannelService,
    expected_channel_slug: str,
):
    """Test that an error has been raised when the value for channel's slug is
    not valid."""

    with pytest.raises(ChannelSlugInvalidValueError):
        channel_service.create_by_data(
            data={
                'channel': {
                    'name': 'test_channel_name',
                    'slug': expected_channel_slug,
                },
            },
        )
