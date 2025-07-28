from django.contrib.auth import get_user_model

import pytest

from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.channels.models import Channel
from core.apps.posts.models import Post
from core.apps.posts.use_cases.posts.create_post import PostCreateUseCase
from core.apps.users.converters.users import user_to_entity


User = get_user_model()


@pytest.mark.django_db
def test_create_post_channel_not_found_error(create_post_use_case: PostCreateUseCase, user: User):
    """Test that an error has been raised when the channel is not found."""

    with pytest.raises(ChannelNotFoundError):
        create_post_use_case.execute(
            user=user_to_entity(user),
            text='test text',
        )


@pytest.mark.django_db
def test_create_post(create_post_use_case: PostCreateUseCase, channel: Channel):
    """Test that the post has been created."""

    expected_post_text = 'test text 1234567'

    assert Post.objects.all().count() == 0

    created_post = create_post_use_case.execute(
        user=user_to_entity(channel.user),
        text=expected_post_text,
    )

    retrieved_post = Post.objects.all().last()

    assert retrieved_post is not None
    assert created_post.text == expected_post_text
    assert created_post.author_id == channel.pk
    assert created_post.created_at == retrieved_post.created_at
    assert created_post.pk == retrieved_post.pk
