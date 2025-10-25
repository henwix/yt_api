import random

import pytest
from django.db.models import Count
from faker import Faker

from core.apps.posts.exceptions import PostNotFoundError
from core.apps.posts.models import (
    Post,
    PostCommentItem,
    PostCommentLikeItem,
)
from core.apps.posts.use_cases.posts_comments.get_list_comments import GetPostCommentsUseCase
from core.tests.factories.posts import (
    PostCommentLikeModelFactory,
    PostCommentModelFactory,
)

fake = Faker()


@pytest.mark.django_db
def test_get_list_comments_post_exception(get_post_comments_use_case: GetPostCommentsUseCase):
    """Test that an exception is raised when the post is not found."""

    with pytest.raises(PostNotFoundError):
        get_post_comments_use_case.execute(
            post_id=fake.uuid4(),
        )


@pytest.mark.django_db
@pytest.mark.parametrize('expected_comments', [1, 3, 8, 10])
def test_get_list_comments_retrieved(
    get_post_comments_use_case: GetPostCommentsUseCase,
    post: Post,
    expected_comments: int,
):
    """Test that the comments have been retrieved."""

    # Create comments
    PostCommentModelFactory.create_batch(size=expected_comments, post=post, reply_level=0)

    comments = get_post_comments_use_case.execute(post_id=post.pk)

    assert len(comments) == expected_comments, f'Expected {expected_comments} comments, got {len(comments)}'

    for comment in comments:
        assert comment.reply_level == 0
        assert comment.reply_comment_id is None
        assert comment.post_id == post.pk
        assert comment.likes_count == 0
        assert comment.replies_count == 0


@pytest.mark.django_db
def test_get_list_comments_retrieved_with_replies(
    get_post_comments_use_case: GetPostCommentsUseCase,
    post: Post,
):
    """Test that the replies have been retrieved and 'replies_count' field is
    correct."""

    # Create comments and replies for them
    created_comments = PostCommentModelFactory.create_batch(size=10, post=post, reply_level=0)
    for comment in created_comments:
        PostCommentModelFactory.create_batch(
            size=random.choice(range(1, 11)),  # noqa
            post=post,
            reply_comment=comment,
            reply_level=1,
        )  # noqa

    # Retrieve comments via use case
    retrieved_comments = get_post_comments_use_case.execute(post_id=post.pk)

    # Retrieve 'replies_count' fields from the 'retrieved_comments' and save them in the dict
    retrieved_replies = {comment.pk: comment.replies_count for comment in retrieved_comments}

    # Retrieve 'replies_count' fields from the database and save them in the dict
    expected_replies = (
        PostCommentItem.objects.filter(reply_level=1)
        .values(
            'reply_comment',
        )
        .annotate(replies_count=Count('pk'))
    )

    # Compare 'replies_count' fields from database and use case
    for expected_reply in expected_replies:
        assert expected_reply['replies_count'] == retrieved_replies[expected_reply['reply_comment']]


@pytest.mark.django_db
def test_get_list_comments_retrieved_with_likes(
    get_post_comments_use_case: GetPostCommentsUseCase,
    post: Post,
):
    """Test that the comments have been retrieved and 'likes_count' field is
    correct."""

    # Create comments and likes for them
    created_comments = PostCommentModelFactory.create_batch(size=5, post=post, reply_level=0)
    for comment in created_comments:
        PostCommentLikeModelFactory.create_batch(
            size=20,
            comment=comment,
        )  # noqa

    # Retrieve comments via use case
    retrieved_comments = get_post_comments_use_case.execute(post_id=post.pk)

    # Retrieve 'likes_count' fields from the 'retrieved_comments' and save them in the dict
    retrieved_likes = {comment.pk: comment.likes_count for comment in retrieved_comments}

    # Retrieve 'likes_count' fields from the database and save them in the dict
    expected_likes = (
        PostCommentLikeItem.objects.filter(is_like=True)
        .values(
            'comment_id',
        )
        .annotate(likes_count=Count('pk'))
    )

    assert len(retrieved_likes) == len(expected_likes)

    # Compare 'likes_count' fields from database and use case
    for expected_like in expected_likes:
        assert expected_like['likes_count'] == retrieved_likes[expected_like['comment_id']]
