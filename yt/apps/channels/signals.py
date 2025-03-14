from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Channel


@receiver(signal=[post_save, pre_delete], sender=Channel)
def invalidate_channel_cache_and_delete_avatar(sender, instance, **kwargs):
    cache.delete(f"retrieve_channel_{instance.user.pk}")

    signal = kwargs.get("signal")

    if signal is pre_delete and instance.channel_avatar:
        instance.channel_avatar.delete()
        # FIXME: видосы не удаляются
        instance.videos.delete()
