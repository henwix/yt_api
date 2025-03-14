from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.


class Channel(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="channel")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=40, unique=True, blank=True)
    country = models.CharField(max_length=40)
    subscriptions = models.ManyToManyField(
        to="self", symmetrical=False, through="SubscriptionItem", related_name="subscribers", blank=True
    )
    description = models.TextField(blank=True)
    channel_avatar = models.ImageField(upload_to="channel_avatars", null=True, blank=True)

    def __str__(self):
        return f"{self.name} | {self.slug}"


class SubscriptionItem(models.Model):
    subscriber = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="following")
    subscribed_to = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["subscriber", "subscribed_to"], name="unique_subscription")]

    def __str__(self):
        return f"{self.subscriber} subscribed to {self.subscribed_to}"
