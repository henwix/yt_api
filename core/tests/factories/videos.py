from datetime import datetime

import factory
from apps.videos.models import Video, generate_video_link
from factory.django import DjangoModelFactory
from faker import Faker

from .channels import ChannelModelFactory
from .common import factory_lazy_function

fake = Faker()


class VideoModelFactory(DjangoModelFactory):
    class Meta:
        model = Video

    video_id = factory.LazyFunction(generate_video_link)
    author = factory.SubFactory(ChannelModelFactory)
    name = factory_lazy_function(fake.text, 40)
    created_at = factory.LazyFunction(datetime.now)
