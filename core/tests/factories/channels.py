import factory
from factory.django import DjangoModelFactory
from faker import Faker

from core.apps.channels.models import (
    Channel,
    SubscriptionItem,
)
from core.apps.users.models import CustomUser
from core.tests.factories.common import factory_lazy_function

fake = Faker()


class UserModelFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')


class ChannelModelFactory(DjangoModelFactory):
    class Meta:
        model = Channel

    user = factory.SubFactory(UserModelFactory)
    name = factory_lazy_function(fake.first_name, max_length=40)
    slug = factory_lazy_function(fake.slug, max_length=40)
    description = factory.Faker('text')
    country = factory_lazy_function(fake.country, max_length=40)


class SubscriptionItemModelFactory(DjangoModelFactory):
    class Meta:
        model = SubscriptionItem

    subscriber = factory.SubFactory(ChannelModelFactory)
    subscribed_to = factory.SubFactory(ChannelModelFactory)
