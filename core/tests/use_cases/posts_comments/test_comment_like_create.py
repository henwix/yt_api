from django.contrib.auth import get_user_model

import pytest

from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.channels.models import Channel
from core.apps.common.exceptions.comments import CommentNotFoundError
from core.apps.posts.models import (
    PostCommentItem,
    PostCommentLikeItem,
)
from core.apps.posts.use_cases.posts_comments.like_create import PostCommentLikeCreateUseCase
from core.apps.users.converters.users import user_to_entity
from core.tests.factories.posts import PostCommentLikeModelFactory


User = get_user_model()


@pytest.mark.django_db
def test_post_comment_like_create_channel_exception(
    post_comment_like_create_use_case: PostCommentLikeCreateUseCase,
    user: User,
):
    """Test that an exception is raised when the channel is not found."""

    with pytest.raises(ChannelNotFoundError):
        post_comment_like_create_use_case.execute(user=user_to_entity(user), comment_id=None, is_like=None)


@pytest.mark.django_db
def test_post_comment_like_create_post_exception(
    post_comment_like_create_use_case: PostCommentLikeCreateUseCase,
    channel: Channel,
):
    """Test that an exception is raised when the post is not found."""

    with pytest.raises(CommentNotFoundError):
        post_comment_like_create_use_case.execute(
            user=user_to_entity(channel.user),
            comment_id=1,
            is_like=None,
        )


@pytest.mark.parametrize('expected_is_like', [True, False])
@pytest.mark.django_db
def test_post_comment_like_created(
    post_comment_like_create_use_case: PostCommentLikeCreateUseCase,
    channel: Channel,
    post_comment: PostCommentItem,
    expected_is_like: bool,
):
    """Test that new like has been created."""

    assert not PostCommentLikeItem.objects.filter(
        author=channel, comment=post_comment, is_like=expected_is_like,
    ).exists()

    result = post_comment_like_create_use_case.execute(
        user=user_to_entity(channel.user),
        comment_id=post_comment.pk,
        is_like=expected_is_like,
    )

    assert result == {'status': 'success', 'is_like': expected_is_like}
    assert PostCommentLikeItem.objects.filter(
        author=channel, comment=post_comment, is_like=expected_is_like,
    ).exists()


@pytest.mark.parametrize('initial_is_like, expected_is_like', ([True, False], [False, True]))
@pytest.mark.django_db
def test_post_create_like_updated(
    post_comment_like_create_use_case: PostCommentLikeCreateUseCase,
    channel: Channel,
    post_comment: PostCommentItem,
    initial_is_like: bool,
    expected_is_like: bool,
):
    """Test that 'is_like' status has been updated."""

    PostCommentLikeModelFactory.create(author=channel, comment=post_comment, is_like=initial_is_like)

    assert PostCommentLikeItem.objects.filter(
        author=channel, comment=post_comment, is_like=initial_is_like,
    ).exists()
    assert not PostCommentLikeItem.objects.filter(
        author=channel, comment=post_comment, is_like=expected_is_like,
    ).exists()

    post_comment_like_create_use_case.execute(
        user=user_to_entity(channel.user),
        comment_id=post_comment.pk,
        is_like=expected_is_like,
    )

    assert not PostCommentLikeItem.objects.filter(
        author=channel, comment=post_comment, is_like=initial_is_like,
    ).exists()
    assert PostCommentLikeItem.objects.filter(
        author=channel, comment=post_comment, is_like=expected_is_like,
    ).exists()

    post_comment_like_create_use_case.execute(
        user=user_to_entity(channel.user),
        comment_id=post_comment.pk,
        is_like=initial_is_like,
    )

    assert PostCommentLikeItem.objects.filter(
        author=channel, comment=post_comment, is_like=initial_is_like,
    ).exists()
    assert not PostCommentLikeItem.objects.filter(
        author=channel, comment=post_comment, is_like=expected_is_like,
    ).exists()


@pytest.mark.parametrize('is_like', [True, False])
@pytest.mark.django_db
def test_post_create_like_duplicates(
    post_comment_like_create_use_case: PostCommentLikeCreateUseCase,
    channel: Channel,
    post_comment: PostCommentItem,
    is_like: bool,
):
    """Test that 'is_like' status is the same and duplicate are not created."""

    PostCommentLikeModelFactory.create(author=channel, comment=post_comment, is_like=is_like)

    assert PostCommentLikeItem.objects.filter(author=channel, comment=post_comment, is_like=is_like).count() == 1

    post_comment_like_create_use_case.execute(
        user=user_to_entity(channel.user),
        comment_id=post_comment.pk,
        is_like=is_like,
    )

    assert PostCommentLikeItem.objects.filter(author=channel, comment=post_comment, is_like=is_like).count() == 1
