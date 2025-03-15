import random
from datetime import timedelta

from apps.videos.models import Video
from django.db.models import F


def run():
    videos = Video.objects.all()
    video = random.choice(videos)
    video.created_at = F('created_at') - timedelta(days=302)
    video.save()
