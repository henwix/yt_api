from logging import Logger

from django.conf import settings
from django.db.models.signals import (
    post_save,
    pre_delete,
)
from django.dispatch import receiver

import punq

from core.apps.channels.models import Channel
from core.apps.common.providers.cache import BaseCacheProvider
from core.apps.common.providers.files import BaseCeleryFileProvider
from core.apps.videos.models import Video
from core.project.containers import get_container


@receiver(signal=[post_save], sender=Channel)
def invalidate_channel_cache(instance, created, **kwargs):
    """This signal will delete channel's cache if channel instance has been
    updated."""

    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)
    cache_provider: BaseCacheProvider = container.resolve(BaseCacheProvider)

    if not created:
        cache_provider.delete(f'retrieve_channel_{instance.user.pk}')
        logger.info('Cache for %s deleted', instance.name)


# FIXME: fix number of requests when deleting channel because of CASCADE field in model
@receiver(signal=[pre_delete], sender=Channel)
def delete_channel_files_signal(instance, **kwargs):
    """This signal will collect channel's related videos and avatar into list
    and call celery task to delete them via boto3."""

    container: punq.Container = get_container()
    celery_provider: BaseCeleryFileProvider = container.resolve(BaseCeleryFileProvider)

    # Define empty 'files' and 'cache_keys' lists
    files = []
    cache_keys = []

    # Iterate all related videos and add their keys in 'files' and 'cache_keys' lists
    for v in instance.videos.all():
        if v.s3_key is not None and v.upload_status == Video.UploadStatus.FINISHED:
            files.append({'Key': v.s3_key})
            cache_keys.append(settings.CACHE_KEYS['s3_video_url'] + v.s3_key)

    # If avatar_s3_key exists it'll append to 'files' list and 'cache_keys' list
    if instance.avatar_s3_key is not None:
        files.append({'Key': instance.avatar_s3_key})
        cache_keys.append(settings.CACHE_KEYS['s3_avatar_url_' + instance.avatar_s3_key])

    if files:
        celery_provider.delete_objects(objects=files, cache_keys=cache_keys)
