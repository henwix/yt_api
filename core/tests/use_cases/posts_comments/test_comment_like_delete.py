import pytest

from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.channels.models import Channel
from core.apps.common.exceptions.comments import (
    CommentLikeNotFoundError,
    CommentNotFoundError,
)
from core.apps.posts.models import (
    PostCommentItem,
    PostCommentLikeItem,
)
from core.apps.posts.use_cases.posts_comments.like_delete import PostCommentLikeDeleteUseCase
from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser
from core.tests.factories.posts import PostCommentLikeModelFactory


@pytest.mark.django_db
def test_post_delete_like_channel_not_found_error(
    post_comment_like_delete_use_case: PostCommentLikeDeleteUseCase,
    user: CustomUser,
):
    """That that an 'ChannelNotFoundError' error has been raised."""

    with pytest.raises(ChannelNotFoundError):
        post_comment_like_delete_use_case.execute(
            user_to_entity(user),
            None,
        )


@pytest.mark.django_db
def test_post_delete_like_post_not_found_error(
    post_comment_like_delete_use_case: PostCommentLikeDeleteUseCase,
    channel: Channel,
):
    """That that an 'CommentNotFoundError' error has been raised."""

    with pytest.raises(CommentNotFoundError):
        post_comment_like_delete_use_case.execute(
            user=user_to_entity(channel.user),
            comment_id=1,
        )


@pytest.mark.django_db
def test_post_delete_like_like_not_found_error(
    post_comment_like_delete_use_case: PostCommentLikeDeleteUseCase,
    channel: Channel,
    post_comment: PostCommentItem,
):
    """That that an 'CommentLikeNotFoundError' error has been raised."""

    with pytest.raises(CommentLikeNotFoundError):
        post_comment_like_delete_use_case.execute(
            user=user_to_entity(channel.user),
            comment_id=post_comment.pk,
        )


@pytest.mark.parametrize('expected_like', [True, False])
@pytest.mark.django_db
def test_post_delete_like_deleted(
    post_comment_like_delete_use_case: PostCommentLikeDeleteUseCase,
    channel: Channel,
    post_comment: PostCommentItem,
    expected_like: bool,
):
    """That that like has been deleted."""

    PostCommentLikeModelFactory.create(author=channel, comment=post_comment, is_like=expected_like)

    assert PostCommentLikeItem.objects.filter(author=channel, comment=post_comment, is_like=expected_like).exists()

    post_comment_like_delete_use_case.execute(
        user=user_to_entity(channel.user),
        comment_id=post_comment.pk,
    )

    assert not PostCommentLikeItem.objects.filter(author=channel, comment=post_comment, is_like=expected_like).exists()
