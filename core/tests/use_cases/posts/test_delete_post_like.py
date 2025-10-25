import pytest
from django.contrib.auth import get_user_model
from faker import Faker

from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.channels.models import Channel
from core.apps.posts.exceptions import (
    PostLikeNotFoundError,
    PostNotFoundError,
)
from core.apps.posts.models import (
    Post,
    PostLikeItem,
)
from core.apps.posts.use_cases.posts.delete_post_like import PostLikeDeleteUseCase
from core.apps.users.converters.users import user_to_entity
from core.tests.factories.posts import PostLikeModelFactory

fake: Faker = Faker()
User = get_user_model()


@pytest.mark.django_db
def test_post_delete_like_channel_not_found_error(
    post_like_delete_use_case: PostLikeDeleteUseCase,
    user: User,
):
    """That that an 'ChannelNotFoundError' error has been raised."""

    with pytest.raises(ChannelNotFoundError):
        post_like_delete_use_case.execute(
            user_to_entity(user),
            None,
        )


@pytest.mark.django_db
def test_post_delete_like_post_not_found_error(
    post_like_delete_use_case: PostLikeDeleteUseCase,
    channel: Channel,
):
    """That that an 'PostNotFoundError' error has been raised."""

    with pytest.raises(PostNotFoundError):
        post_like_delete_use_case.execute(
            user=user_to_entity(channel.user),
            post_id=fake.uuid4(),
        )


@pytest.mark.django_db
def test_post_delete_like_like_not_found_error(
    post_like_delete_use_case: PostLikeDeleteUseCase,
    channel: Channel,
    post: Post,
):
    """That that an 'PostLikeNotFoundError' error has been raised."""

    with pytest.raises(PostLikeNotFoundError):
        post_like_delete_use_case.execute(
            user=user_to_entity(channel.user),
            post_id=post.pk,
        )


@pytest.mark.parametrize('expected_like', [True, False])
@pytest.mark.django_db
def test_post_delete_like_deleted(
    post_like_delete_use_case: PostLikeDeleteUseCase,
    channel: Channel,
    post: Post,
    expected_like: bool,
):
    """That that like has been deleted."""

    PostLikeModelFactory.create(channel=channel, post=post, is_like=expected_like)

    assert PostLikeItem.objects.filter(channel=channel, post=post, is_like=expected_like).exists()

    post_like_delete_use_case.execute(
        user=user_to_entity(channel.user),
        post_id=post.pk,
    )

    assert not PostLikeItem.objects.filter(channel=channel, post=post, is_like=expected_like).exists()
