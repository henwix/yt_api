import random
import string
from django.db import models
from apps.channels.models import Channel


class PublicAndUnlistedVideosManager(models.Manager):
    """
    Custom manager to return public and unlisted videos.
    """

    def get_queryset(self):
        return super().get_queryset().filter(status__in=[Video.VideoStatus.UNLISTED, Video.VideoStatus.PUBLIC])


def generate_video_link():
    chars = string.digits + string.ascii_letters

    while True:
        link = ''.join(random.choices(chars, k=11))
        if not Video.objects.filter(video_id=link).exists():
            return link


class Video(models.Model):
    class VideoStatus(models.TextChoices):
        PRIVATE = 'PRIVATE', 'Private'
        UNLISTED = 'UNLISTED', 'Unlisted'
        PUBLIC = 'PUBLIC', 'Public'

    video_id = models.CharField(
        max_length=11, unique=True, 
        primary_key=True, 
        default=generate_video_link, 
        editable=False
    )
    author = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='videos')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    yt_link = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=VideoStatus.choices, default=VideoStatus.PUBLIC)
    file = models.FileField(upload_to='videos', blank=True, null=True)

    # managers
    objects = models.Manager()
    public_unlisted_videos = PublicAndUnlistedVideosManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class VideoLike(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,  related_name='liked_videos')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['channel', 'video'],
                name='unique_channel_video_like'
            ),
        ]
    
    def __str__(self):
        return f"Like on video: {self.video}, by {self.channel}"


class VideoView(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='views')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='video_views', blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View on video: {self.video}, by ch: {getattr(self, 'channel')} | ip: {getattr(self, 'ip_address')}"


class VideoComment(models.Model):
    author = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='video_comments')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Channel, related_name='liked_video_comments', blank=True)

    def __str__(self):
        return f"Comment by {self.author}, video: {self.video}"