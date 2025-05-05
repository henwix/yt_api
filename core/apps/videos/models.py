import random
import string

from django.db import models

from core.apps.channels.models import Channel


def generate_video_link():
    """Function to generate unique video's links."""

    chars = string.digits + string.ascii_letters + '-' + '_'

    while True:
        link = ''.join(random.choices(chars, k=11))  # noqa
        if not Video.objects.filter(video_id=link).exists():
            return link


def generate_playlist_link():
    """Function to generate unique playlist links."""

    chars = string.digits + string.ascii_letters + '-' + '_'
    return ''.join(random.choices(chars, k=32))  # noqa


class PublicAndUnlistedVideosManager(models.Manager):
    """Custom manager to return public and unlisted videos."""

    def get_queryset(self):
        return super().get_queryset().filter(status__in=[Video.VideoStatus.UNLISTED, Video.VideoStatus.PUBLIC])


class Video(models.Model):
    class VideoStatus(models.TextChoices):
        PRIVATE = 'PRIVATE', 'Private'
        UNLISTED = 'UNLISTED', 'Unlisted'
        PUBLIC = 'PUBLIC', 'Public'

    class UploadStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        FINISHED = 'FINISHED', 'Finished'

    video_id = models.CharField(
        max_length=11,
        unique=True,
        primary_key=True,
        default=generate_video_link,
        editable=False,
    )
    author = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='videos', db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    upload_id = models.CharField(null=True, blank=True)
    s3_key = models.CharField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=VideoStatus.choices, default=VideoStatus.PUBLIC)
    upload_status = models.CharField(choices=UploadStatus.choices, default=UploadStatus.PENDING)
    is_reported = models.BooleanField(default=False)

    # managers
    objects = models.Manager()
    public_unlisted_videos = PublicAndUnlistedVideosManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class VideoLike(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='liked_videos', db_index=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes', db_index=True)
    is_like = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['channel', 'video'], name='unique_channel_video_like'),
        ]

    def __str__(self):
        return f'Like on video: {self.video}, by {self.channel}'


class VideoView(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='views', db_index=True)
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='video_views',
        blank=True,
        null=True,
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'View on video{self.video} by {getattr(self, "channel")}'


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_updated = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f'Comment #{id}'


class VideoComment(Comment):
    reply_level_choices = [
        (0, 0),
        (1, 1),
    ]

    author = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='video_comments', db_index=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments', db_index=True)
    comment = models.ForeignKey(to='self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    reply_level = models.PositiveIntegerField(choices=reply_level_choices, default=0, db_index=True)
    likes = models.ManyToManyField(Channel, through='VideoCommentLikeItem', db_index=True)

    def __str__(self):
        return f'Comment by {self.author}, video: {self.video}'


class VideoCommentLikeItem(models.Model):
    author = models.ForeignKey(to=Channel, on_delete=models.CASCADE, related_name='liked_video_comments')
    comment = models.ForeignKey(to=VideoComment, on_delete=models.CASCADE, related_name='likes_items', db_index=True)
    is_like = models.BooleanField(default=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'comment'], name='unique_comment_like'),
        ]

    def __str__(self):
        return f'Comment like by {self.author_id} to comment {self.comment_id}'


class VideoHistory(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='history', db_index=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, db_index=True)
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['channel', 'video'], name='unique_watch_history')]

    def __str__(self):
        return f'Video {self.video_id} in history {self.channel_id}'


class Playlist(models.Model):
    class StatusChoices(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        PRIVATE = 'PRIVATE', 'Private'

    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='playlists', db_index=True)
    videos = models.ManyToManyField(Video, through='PlaylistItem', db_index=True)
    id = models.CharField(
        primary_key=True,
        max_length=32,
        default=generate_playlist_link,
        unique=True,
        editable=False,
        db_index=True,
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=7, choices=StatusChoices.choices, default=StatusChoices.PRIVATE)

    def __str__(self):
        return f'Playlist: {self.title}'


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='items')
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['playlist', 'video'], name='playlist_item_unique')]

    def __str__(self):
        return f'Video {self.video_id} in playlist {self.playlist_id}'
