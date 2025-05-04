from logging import Logger

from django.core.cache import cache
from django.db.models.signals import (
    post_save,
    pre_delete,
)
from django.dispatch import receiver

import punq

from core.apps.common.providers.files import BaseCeleryFileProvider
from core.apps.videos.models import Video
from core.project.containers import get_container

from .models import Channel


@receiver(signal=[post_save], sender=Channel)
def invalidate_channel_cache(instance, created, **kwargs):
    """This signal will delete channel's cache if channel instance has been
    updated."""

    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)

    if not created:
        cache.delete(f'retrieve_channel_{instance.user.pk}')
        logger.info('Cache for %s deleted', instance.name)


# FIXME: починить количество запросов на удаление канала(мб через транзакции или как-то вручную удалять связи)
@receiver(signal=[pre_delete], sender=Channel)
def delete_channel_files_signal(instance, **kwargs):
    """This signal will collect channel's related videos and avatar into list
    and call celery task to delete them via boto3."""

    container: punq.Container = get_container()
    celery_provider: BaseCeleryFileProvider = container.resolve(BaseCeleryFileProvider)

    # Define empty 'files' list
    files = []

    # Collect all related videos to list and if it's not empty extend to 'files'
    if instance.videos.exists():
        videos = [
            {'Key': v.s3_key} for v in instance.videos.all() if v.upload_status == Video.UploadStatus.FINISHED
        ]
        files.extend(videos)

    # If avatar_s3_key exists it'll append to 'files' list
    if instance.avatar_s3_key is not None:
        files.append({'Key': instance.avatar_s3_key})

    if files:
        celery_provider.delete_objects(objects=files)
