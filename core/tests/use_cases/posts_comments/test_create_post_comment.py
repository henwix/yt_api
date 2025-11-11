import pytest

from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.channels.models import Channel
from core.apps.posts.converters.posts import post_to_entity
from core.apps.posts.entities.comments import PostCommentEntity
from core.apps.posts.models import (
    Post,
    PostCommentItem,
)
from core.apps.posts.use_cases.posts_comments.create_comment import CreatePostCommentUseCase
from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser


@pytest.mark.django_db
def test_create_post_comment_channel_not_found_error(
    create_post_comment_use_case: CreatePostCommentUseCase,
    user: CustomUser,
):
    """Test that an error is raised when the channel is not found."""

    with pytest.raises(ChannelNotFoundError):
        create_post_comment_use_case.execute(
            user=user_to_entity(user),
            post=None,
            text=None,
            reply_comment_id=None,
        )


@pytest.mark.parametrize('expected_text', ['Test comment', 'Test comment 2'])
@pytest.mark.django_db
def test_create_post_comment_created(
    create_post_comment_use_case: CreatePostCommentUseCase,
    channel: Channel,
    post: Post,
    expected_text: str,
):
    """Test that the comment has been created."""

    assert not PostCommentItem.objects.filter(post=post, author=channel).exists()

    created_comment: PostCommentEntity = create_post_comment_use_case.execute(
        user=user_to_entity(channel.user),
        post=post_to_entity(post),
        text=expected_text,
        reply_comment_id=None,
    )

    assert created_comment.text == expected_text
    assert created_comment.author_id == channel.pk
    assert created_comment.post_id == post.pk
    assert created_comment.reply_level == 0
    assert created_comment.reply_comment_id is None
    assert created_comment.is_updated is False
    assert PostCommentItem.objects.filter(post=post, author=channel, text=expected_text, reply_level=0).exists()


@pytest.mark.parametrize('expected_text', ['Test reply comment', 'Test reply comment 2'])
@pytest.mark.django_db
def test_create_post_comment_reply_created(
    create_post_comment_use_case: CreatePostCommentUseCase,
    channel: Channel,
    post: Post,
    post_comment: PostCommentItem,
    expected_text: str,
):
    """Test that the reply comment has been created."""

    assert not PostCommentItem.objects.filter(post=post, author=channel, reply_comment=post_comment).exists()

    created_reply: PostCommentEntity = create_post_comment_use_case.execute(
        user=user_to_entity(channel.user),
        post=post_to_entity(post),
        text=expected_text,
        reply_comment_id=post_comment.pk,
    )

    assert created_reply.text == expected_text
    assert created_reply.author_id == channel.pk
    assert created_reply.post_id == post.pk
    assert created_reply.reply_level == 1
    assert created_reply.reply_comment_id == post_comment.pk
    assert created_reply.is_updated is False
    assert PostCommentItem.objects.filter(
        post=post,
        author=channel,
        text=expected_text,
        reply_level=1,
        reply_comment=post_comment,
    ).exists()
