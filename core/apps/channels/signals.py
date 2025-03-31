import logging

from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Channel
from .tasks import delete_channel_files_task

log = logging.getLogger(__name__)


def _delete_channel_cache(instance):
    """Mixin to delete channel's cache"""

    cache.delete(f'retrieve_channel_{instance.user.pk}')
    log.info('Cache for %s deleted', instance.name)


@receiver(signal=[post_save], sender=Channel)
def invalidate_channel_cache(instance, created, **kwargs):
    """This signal will delete channel's cache if channel instance has been updated"""

    if not created:
        # Delete channel's cache
        _delete_channel_cache(instance)


# FIXME: починить количество запросов на удаление канала(мб через транзакции или как-то вручную удалять связи)
@receiver(signal=[pre_delete], sender=Channel)
def delete_channel_files_signal(instance, **kwargs):
    """
    This signal will collect channel's related videos and avatar into list and call celery task to delete them via boto3
    """

    # Delete channel's cache
    _delete_channel_cache(instance)

    # Define empty 'files' list
    files = []

    # Collect all related videos to list and if it's not empty extend to files
    if instance.videos.exists():
        videos = [{'Key': video.file.name} for video in instance.videos.all() if video.file]
        files.extend(videos)
    # If channel_avatar exists it'll append to files list
    if instance.channel_avatar and instance.channel_avatar.name:
        files.append({'Key': instance.channel_avatar.name})

    if files:
        log.info('Start deleting files task for %s', instance.name)
        delete_channel_files_task.apply_async(args=[files], queue='media-queue')
    else:
        log.info('No files to delete for %s', instance.name)
