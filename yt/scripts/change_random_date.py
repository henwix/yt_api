from apps.videos.models import Video
import random
from django.db.models import F
from datetime import timedelta


def run():
    videos = Video.objects.all()
    video = random.choice(videos)
    video.created_at = F('created_at') - timedelta(days=302)
    video.save()
