from django.dispatch import (
    receiver,
    Signal,
)

import punq

from core.apps.common.constants import CACHE_KEYS
from core.apps.common.providers.files import BaseCeleryFileProvider
from core.apps.videos.models import Video
from core.project.containers import get_container


video_pre_delete = Signal()


@receiver(signal=video_pre_delete)
def delete_existing_s3_video_signal(instance, **kwargs):
    container: punq.Container = get_container()
    celery_provider: BaseCeleryFileProvider = container.resolve(BaseCeleryFileProvider)

    if instance.s3_key and instance.upload_status == Video.UploadStatus.FINISHED:
        celery_provider.delete_object_by_key(
            key=instance.s3_key,
            cache_key=CACHE_KEYS['s3_video_url'] + instance.s3_key,
        )
