import factory
from factory.django import DjangoModelFactory

from core.apps.videos.models import (
    VideoComment,
    VideoCommentLikeItem,
)
from core.tests.factories.channels import ChannelModelFactory
from core.tests.factories.videos import VideoModelFactory


class VideoCommentModelFactory(DjangoModelFactory):
    class Meta:
        model = VideoComment

    author = factory.SubFactory(ChannelModelFactory)
    video = factory.SubFactory(VideoModelFactory)
    text = factory.Faker('text')


class VideoCommentLikeFactoryItem(DjangoModelFactory):
    class Meta:
        model = VideoCommentLikeItem

    author = factory.SubFactory(ChannelModelFactory)
    comment = factory.SubFactory(VideoCommentModelFactory)
