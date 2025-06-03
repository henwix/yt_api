import pytest

from core.apps.channels.models import Channel
from core.apps.videos.converters.comments import video_comment_from_entity
from core.apps.videos.models import (
    Video,
    VideoComment,
    VideoCommentLikeItem,
)
from core.apps.videos.services.comments import BaseCommentService
from core.tests.factories.video_comments import VideoCommentModelFactory


@pytest.mark.django_db
def test_comments_retrieved_by_video_id(video: Video, comment_service: BaseCommentService):
    expected_value = 7
    VideoCommentModelFactory.create_batch(
        size=expected_value,
        video=video,
    )
    qs = comment_service.get_comments_by_video_id(video_id=video.video_id)

    assert qs.count() == expected_value


@pytest.mark.django_db
def test_comment_retrieved_by_id(comment_service: BaseCommentService):
    expected_comment = VideoCommentModelFactory()
    comment_dto = video_comment_from_entity(comment_service.get_by_id_or_404(id=expected_comment.pk))

    assert expected_comment == comment_dto


@pytest.mark.django_db
def test_replies_retrieved_by_comment_id(comment: VideoComment, comment_service: BaseCommentService):
    expected_value = 6
    VideoCommentModelFactory.create_batch(
        size=expected_value,
        comment=comment,
        reply_level=1,
    )
    qs = comment_service.get_replies_by_comment_id(comment_id=comment.pk)

    assert qs.count() == expected_value


@pytest.mark.django_db
def test_comment_updated_status_changed(comment: VideoComment, comment_service: BaseCommentService):
    assert comment.is_updated is False
    comment_service.change_updated_status(comment_id=comment.pk, is_updated=True)
    assert VideoComment.objects.filter(id=comment.pk, is_updated=True).exists()


@pytest.mark.django_db
def test_like_status_changed(comment_service: BaseCommentService, like: VideoCommentLikeItem):
    assert like.is_like is True
    comment_service.update_like_status(
        like_id=like.pk,
        is_like=False,
    )
    assert VideoCommentLikeItem.objects.filter(id=like.pk, is_like=False).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('is_like', [True, False])
def test_like_created(
    comment_service: BaseCommentService,
    channel: Channel,
    comment: VideoComment,
    is_like: bool,
):
    retrieved_like, created = comment_service.like_get_or_create(
        author=channel,
        comment=comment,
        is_like=is_like,
    )

    assert created is True
    assert retrieved_like.author_id == channel.pk
    assert retrieved_like.comment_id == comment.pk
    assert retrieved_like.is_like == is_like


@pytest.mark.django_db
def test_like_retrieved(comment_service: BaseCommentService, like: VideoCommentLikeItem):
    retrieved_like, created = comment_service.like_get_or_create(
        author=like.author,
        comment=like.comment,
        is_like=like.is_like,
    )

    assert created is False
    assert retrieved_like.author_id == like.author_id
    assert retrieved_like.comment_id == like.comment_id
    assert retrieved_like.is_like == like.is_like


@pytest.mark.django_db
def test_like_deleted(comment_service: BaseCommentService, like: VideoCommentLikeItem):
    assert VideoCommentLikeItem.objects.filter(author=like.author, comment=like.comment).exists()

    comment_service.like_delete(
        author=like.author,
        comment=like.comment,
    )

    assert not VideoCommentLikeItem.objects.filter(author=like.author, comment=like.comment).exists()
