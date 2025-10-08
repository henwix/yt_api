from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _


class Channel(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='channel', db_index=True)
    name = models.CharField(max_length=100, help_text=_('Channel name'))
    slug = models.SlugField(max_length=40, unique=True, help_text=_('Channel slug'))
    description = models.TextField(blank=True, null=True, help_text=_('Channel description'))
    country = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        help_text=_('Country where the channel is located'),
    )
    subscriptions = models.ManyToManyField(
        to='self', symmetrical=False, through='SubscriptionItem', related_name='subscribers', blank=True,
    )
    avatar_s3_key = models.CharField(max_length=255, null=True, blank=True, help_text=_('Channel avatar S3 file key'))

    def __str__(self):
        return f'{self.name} | {self.slug}'


class SubscriptionItem(models.Model):
    subscriber = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='following', db_index=True)
    subscribed_to = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='followers', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['subscriber', 'subscribed_to'], name='unique_subscription')]

    def __str__(self):
        return f'{self.subscriber} subscribed to {self.subscribed_to}'
