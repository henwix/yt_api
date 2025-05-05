from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

import punq

from core.apps.common.providers.files import BaseCeleryFileProvider
from core.apps.videos.models import Video
from core.project.containers import get_container


@receiver(signal=[pre_delete], sender=Video)
def delete_s3_video_signal(instance, **kwargs):
    container: punq.Container = get_container()
    celery_provider: BaseCeleryFileProvider = container.resolve(BaseCeleryFileProvider)

    celery_provider.delete_object_by_key(
        key=instance.s3_key,
        cache_key=settings.CACHE_KEYS['s3_video_url'] + instance.s3_key,
    )
