from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import Channel
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.cache import cache


@receiver(signal=[post_save, pre_delete], sender=Channel)
def invalidate_channel_cache_and_delete_avatar(sender, instance, **kwargs):
    cache.delete(f"retrieve_channel_{instance.user.pk}")

    signal = kwargs.get('signal')

    if signal is pre_delete and instance.channel_avatar:
        instance.channel_avatar.delete()

    