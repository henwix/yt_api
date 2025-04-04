from datetime import datetime

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from core.apps.videos.models import Video, VideoView, generate_video_link

from .channels import ChannelModelFactory
from .common import factory_lazy_function

fake = Faker()


class VideoModelFactory(DjangoModelFactory):
    class Meta:
        model = Video

    video_id = factory.LazyFunction(generate_video_link)
    author = factory.SubFactory(ChannelModelFactory)
    name = factory_lazy_function(fake.text, max_length=40)
    created_at = factory.LazyFunction(datetime.now)


class VideoViewModelFactory(DjangoModelFactory):
    class Meta:
        model = VideoView

    video = factory.SubFactory(VideoModelFactory)
    channel = factory.SubFactory(ChannelModelFactory)
