import factory
import factory.fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from core.apps.posts.models import (
    Post,
    PostCommentItem,
    PostCommentLikeItem,
    PostLikeItem,
)
from core.tests.factories.channels import ChannelModelFactory


fake = Faker()


class PostModelFactory(DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(ChannelModelFactory)
    text = factory.Faker('text')


class PostLikeModelFactory(DjangoModelFactory):
    class Meta:
        model = PostLikeItem

    channel = factory.SubFactory(ChannelModelFactory)
    post = factory.SubFactory(PostModelFactory)
    is_like = factory.fuzzy.FuzzyChoice([True, False])


class PostCommentModelFactory(DjangoModelFactory):
    class Meta:
        model = PostCommentItem

    author = factory.SubFactory(ChannelModelFactory)
    post = factory.SubFactory(PostModelFactory)
    text = factory.Faker('text')


class PostCommentLikeModelFactory(DjangoModelFactory):
    class Meta:
        model = PostCommentLikeItem

    author = factory.SubFactory(ChannelModelFactory)
    comment = factory.SubFactory(PostCommentModelFactory)
    is_like = factory.fuzzy.FuzzyChoice([True, False])
