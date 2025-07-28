import random

from django.db.models import Count

import pytest

from core.apps.channels.models import Channel
from core.apps.posts.exceptions import PostAuthorSlugNotProvidedError
from core.apps.posts.models import (
    PostCommentItem,
    PostLikeItem,
)
from core.apps.posts.use_cases.posts.get_channel_posts import GetChannelPostsUseCase
from core.tests.factories.posts import (
    PostCommentModelFactory,
    PostLikeModelFactory,
    PostModelFactory,
)


@pytest.mark.django_db
def test_channel_posts_slug_exception(channel_posts_use_case: GetChannelPostsUseCase):
    """Test that an exception 'PostAuthorSlugNotProvidedError' has been
    raised."""

    with pytest.raises(PostAuthorSlugNotProvidedError):
        channel_posts_use_case.execute(slug=None)


@pytest.mark.parametrize('expected_posts', [1, 3, 5, 10])
@pytest.mark.django_db
def test_channel_posts_retrieved(
    channel_posts_use_case: GetChannelPostsUseCase,
    expected_posts: int,
    channel: Channel,
):
    """Test that created posts were retrieved via use case."""

    PostModelFactory.create_batch(size=expected_posts, author=channel)
    posts = channel_posts_use_case.execute(slug=channel.slug)

    assert posts.count() == expected_posts


@pytest.mark.django_db
def test_channel_posts_retrieved_with_likes(
    channel_posts_use_case: GetChannelPostsUseCase,
    channel: Channel,
):
    """Test that 'likes_count' field from the Post's queryset retrieved
    correctly."""

    # Create posts and likes for them
    created_posts = PostModelFactory.create_batch(size=5, author=channel)
    for post in created_posts:
        PostLikeModelFactory.create_batch(size=20, post=post)

    # Retrieve posts via use case
    retrieved_posts = channel_posts_use_case.execute(slug=channel.slug)

    # Retrieve 'likes_count' fields from the retrieved_posts and save them in the dict
    retrieved_likes = {post.pk: post.likes_count for post in retrieved_posts}

    # Retrieve 'likes_count' fields from the database and save them in the dict
    expected_likes = PostLikeItem.objects.filter(is_like=True).values('post_id').annotate(likes_count=Count('pk'))

    # Compare 'likes_count' fields from database and use case
    for expected_like in expected_likes:
        assert expected_like['likes_count'] == retrieved_likes[expected_like['post_id']]


@pytest.mark.django_db
def test_channel_posts_retrieved_with_comments(
    channel_posts_use_case: GetChannelPostsUseCase,
    channel: Channel,
):
    """Test that 'comments_count' field from the Post's queryset retrieved
    correctly."""

    # Create posts and comments for them
    created_posts = PostModelFactory.create_batch(size=10, author=channel)
    for post in created_posts:
        PostCommentModelFactory.create_batch(size=random.choice(range(1, 11)), post=post)  # noqa

    # Retrieve posts via use case
    retrieved_posts = channel_posts_use_case.execute(slug=channel.slug)

    # Retrieve 'comments_count' fields from the retrieved_posts and save them in the dict
    retrieved_comments = {post.pk: post.comments_count for post in retrieved_posts}

    # Retrieve 'comments_count' fields from the database and save them in the dict
    expected_comments = PostCommentItem.objects.all().values('post_id').annotate(comments_count=Count('pk'))

    # Compare 'comments_count' fields from database and use case
    for expected_comment in expected_comments:
        assert expected_comment['comments_count'] == retrieved_comments[expected_comment['post_id']]
