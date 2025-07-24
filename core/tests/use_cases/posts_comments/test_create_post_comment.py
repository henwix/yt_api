from django.contrib.auth import get_user_model

import pytest

from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.posts.use_cases.posts_comments.create_comment import CreatePostCommentUseCase
from core.apps.users.converters.users import user_to_entity


User = get_user_model()


@pytest.mark.django_db
def test_post_comment_channel_not_found_error(create_post_comment_use_case: CreatePostCommentUseCase, user: User):
    with pytest.raises(ChannelNotFoundError):
        create_post_comment_use_case.execute(
            user=user_to_entity(user),
            post=None,
            text=None,
            reply_comment_id=None,
        )
