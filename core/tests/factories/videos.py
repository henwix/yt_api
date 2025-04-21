import factory
from factory.django import DjangoModelFactory
from faker import Faker

from core.apps.videos.models import (
    Playlist,
    PlaylistItem,
    Video,
    VideoLike,
    VideoView,
)

from .channels import ChannelModelFactory
from .common import factory_lazy_function


fake = Faker()


class VideoModelFactory(DjangoModelFactory):
    class Meta:
        model = Video

    author = factory.SubFactory(ChannelModelFactory)
    name = factory_lazy_function(fake.text, max_length=40)
    description = factory.Faker('text')


class VideoViewModelFactory(DjangoModelFactory):
    class Meta:
        model = VideoView

    video = factory.SubFactory(VideoModelFactory)
    channel = factory.SubFactory(ChannelModelFactory)


class VideoLikeModelFactory(DjangoModelFactory):
    class Meta:
        model = VideoLike

    channel = factory.SubFactory(ChannelModelFactory)
    video = factory.SubFactory(VideoModelFactory)
    is_like = True


class PlaylistModelFactory(DjangoModelFactory):
    class Meta:
        model = Playlist

    channel = factory.SubFactory(ChannelModelFactory)
    title = factory_lazy_function(fake.text, max_length=150)
    description = factory.Faker('text')


class PlaylistItemModelFactory(DjangoModelFactory):
    class Meta:
        model = PlaylistItem

    playlist = factory.SubFactory(PlaylistModelFactory)
    video = factory.SubFactory(VideoModelFactory)
