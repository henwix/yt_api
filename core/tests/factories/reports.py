import factory
import factory.fuzzy
from apps.reports.models import VideoReport
from factory.django import DjangoModelFactory
from faker import Faker

from .channels import ChannelModelFactory
from .videos import VideoModelFactory

fake = Faker()


class VideoReportModelFactory(DjangoModelFactory):
    class Meta:
        model = VideoReport

    video = factory.SubFactory(VideoModelFactory)
    author = factory.SubFactory(ChannelModelFactory)
    reason = factory.fuzzy.FuzzyChoice([i[0] for i in VideoReport.ReportReasons.choices])
    description = factory.Faker('text')
