from django.db.models import Count

import pytest

from core.apps.posts.models import (
    PostCommentItem,
    PostCommentLikeItem,
)
from core.apps.posts.use_cases.posts_comments.get_replies_list_comments import GetPostCommentRepliesUseCase
from core.tests.factories.posts import (
    PostCommentLikeModelFactory,
    PostCommentModelFactory,
)


@pytest.mark.django_db
def test_get_comment_replies_empty_list(
    get_post_comment_replies_use_case: GetPostCommentRepliesUseCase,
    post_comment: PostCommentItem,
):
    """Test that an empty list is returned when there are no replies for the
    comment."""

    replies = get_post_comment_replies_use_case.execute(comment_id=post_comment.pk)
    assert len(replies) == 0


@pytest.mark.parametrize('expected_replies', [2, 4, 7, 10, 12])
@pytest.mark.django_db
def test_get_comment_replies_retrieved(
    get_post_comment_replies_use_case: GetPostCommentRepliesUseCase,
    post_comment: PostCommentItem,
    expected_replies: int,
):
    """Test that the replies have been retrieved."""

    PostCommentModelFactory.create_batch(
        size=expected_replies,
        post=post_comment.post,
        reply_comment=post_comment,
        reply_level=1,
    )
    replies = get_post_comment_replies_use_case.execute(comment_id=post_comment.pk)

    assert len(replies) == expected_replies

    for reply in replies:
        assert reply.reply_level == 1
        assert reply.reply_comment_id == post_comment.pk
        assert reply.post_id == post_comment.post.pk
        assert reply.likes_count == 0
        assert reply.replies_count == 0


@pytest.mark.django_db
def test_get_comment_replies_retrieved_with_likes(
    get_post_comment_replies_use_case: GetPostCommentRepliesUseCase,
    post_comment: PostCommentItem,
):
    """Test that the replies have been retrieved and 'likes_count' field is
    correct."""

    # Create replies and likes for them
    created_replies = PostCommentModelFactory.create_batch(
        size=5,
        post=post_comment.post,
        reply_comment=post_comment,
        reply_level=1,
    )
    for reply in created_replies:
        PostCommentLikeModelFactory.create_batch(
            size=20,
            comment=reply,
        )  # noqa

    # Retrieve replies via use case
    retrieved_replies = get_post_comment_replies_use_case.execute(post_comment.pk)

    # Retrieve 'likes_count' fields from the 'retrieved_replies' and save them in the dict
    retrieved_likes = {reply.pk: reply.likes_count for reply in retrieved_replies}

    # Retrieve 'likes_count' fields from the database and save them in the dict
    expected_likes = PostCommentLikeItem.objects.filter(is_like=True).values(
        'comment_id',
    ).annotate(likes_count=Count('pk'))

    assert len(retrieved_likes) == len(expected_likes)

    # Compare 'likes_count' fields from database and use case
    for expected_like in expected_likes:
        assert expected_like['likes_count'] == retrieved_likes[expected_like['comment_id']]
