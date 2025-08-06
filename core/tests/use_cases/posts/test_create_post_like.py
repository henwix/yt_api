from django.contrib.auth import get_user_model

import pytest
from faker import Faker

from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.channels.models import Channel
from core.apps.posts.exceptions import PostNotFoundError
from core.apps.posts.models import (
    Post,
    PostLikeItem,
)
from core.apps.posts.use_cases.posts.create_post_like import PostLikeCreateUseCase
from core.apps.users.converters.users import user_to_entity
from core.tests.factories.posts import PostLikeModelFactory


fake: Faker = Faker()
User = get_user_model()


@pytest.mark.django_db
def test_post_create_like_channel_not_found_error(
    post_like_create_use_case: PostLikeCreateUseCase,
    user: User,
):
    """That that an 'ChannelNotFoundError' error has been raised."""

    with pytest.raises(ChannelNotFoundError):
        post_like_create_use_case.execute(
            user_to_entity(user),
            None,
            None,
        )


@pytest.mark.django_db
def test_post_create_like_post_not_found_error(
    post_like_create_use_case: PostLikeCreateUseCase,
    channel: Channel,
):
    """That that an 'PostNotFoundError' error has been raised."""

    with pytest.raises(PostNotFoundError):
        post_like_create_use_case.execute(
            user=user_to_entity(channel.user),
            post_id=fake.uuid4(),
            is_like=None,
        )


@pytest.mark.parametrize('expected_is_like', [True, False])
@pytest.mark.django_db
def test_post_create_like_created(
    post_like_create_use_case: PostLikeCreateUseCase,
    channel: Channel,
    post: Post,
    expected_is_like: bool,
):
    """Test that new like has been created."""

    assert not PostLikeItem.objects.filter(channel=channel, post=post).exists()

    result = post_like_create_use_case.execute(
        user=user_to_entity(channel.user),
        post_id=post.pk,
        is_like=expected_is_like,
    )

    assert result == {'detail': 'Success', 'is_like': expected_is_like}
    assert PostLikeItem.objects.filter(channel=channel, post=post, is_like=expected_is_like).exists()


@pytest.mark.parametrize('initial_is_like, expected_is_like', ([True, False], [False, True]))
@pytest.mark.django_db
def test_post_create_like_updated(
    post_like_create_use_case: PostLikeCreateUseCase,
    channel: Channel,
    post: Post,
    initial_is_like: bool,
    expected_is_like: bool,
):
    """Test that 'is_like' status has been updated."""

    PostLikeModelFactory.create(channel=channel, post=post, is_like=initial_is_like)

    assert PostLikeItem.objects.filter(channel=channel, post=post, is_like=initial_is_like).exists()
    assert not PostLikeItem.objects.filter(channel=channel, post=post, is_like=expected_is_like).exists()

    post_like_create_use_case.execute(
        user=user_to_entity(channel.user),
        post_id=post.pk,
        is_like=expected_is_like,
    )

    assert not PostLikeItem.objects.filter(channel=channel, post=post, is_like=initial_is_like).exists()
    assert PostLikeItem.objects.filter(channel=channel, post=post, is_like=expected_is_like).exists()

    post_like_create_use_case.execute(
        user=user_to_entity(channel.user),
        post_id=post.pk,
        is_like=initial_is_like,
    )

    assert PostLikeItem.objects.filter(channel=channel, post=post, is_like=initial_is_like).exists()
    assert not PostLikeItem.objects.filter(channel=channel, post=post, is_like=expected_is_like).exists()


@pytest.mark.parametrize('is_like', [True, False])
@pytest.mark.django_db
def test_post_create_like_duplicates(
    post_like_create_use_case: PostLikeCreateUseCase,
    channel: Channel,
    post: Post,
    is_like: bool,
):
    """Test that 'is_like' status is the same and duplicate are not created."""

    PostLikeModelFactory.create(channel=channel, post=post, is_like=is_like)

    assert PostLikeItem.objects.filter(channel=channel, post=post, is_like=is_like).count() == 1

    post_like_create_use_case.execute(
        user=user_to_entity(channel.user),
        post_id=post.pk,
        is_like=is_like,
    )

    assert PostLikeItem.objects.filter(channel=channel, post=post, is_like=is_like).count() == 1
