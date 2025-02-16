from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
import string
import random
import uuid
from django.db.models import Count
# Create your models here.


class Channel(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='channel')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=40, unique=True, blank=True)
    subscriptions = models.ManyToManyField(
        to="self",
        symmetrical=False, # TODO: write to obsidian
        through="SubscriptionItem", 
        related_name='subscribers', 
        blank=True
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} | {self.slug}"


class SubscriptionItem(models.Model):
    subscriber = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='following')
    subscribed_to = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Model:
        # TODO: узнать шо это
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'subscribed_to'], name='unique_subscription')
        ]

    def __str__(self):
        return f"{self.subscriber} subscribed to {self.subscribed_to}"

def generate_video_link():
    chars = string.digits + string.ascii_letters

    while True:
        link = ''.join(random.choices(chars, k=11))
        if not Video.objects.filter(video_id=link).exists():
            return link


class Video(models.Model):
    # TODO: add dislikes to videos, comments and posts

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
    likes = models.ManyToManyField(Channel, related_name='liked_videos', blank=True)
    yt_link = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=VideoStatus.choices, default=VideoStatus.PUBLIC)

    def __str__(self):
        return self.name
    
    @property
    def likes_count(self):
        return self.likes.count()


class VideoComment(models.Model):
    author = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='video_comments')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Channel, related_name='liked_video_comments', blank=True)

    def __str__(self):
        return f"Comment by {self.author}, video: {self.video}"


# TODO:
# class PlayList(models.Model):
#     name = models.CharField(max_length=100)


class Post(models.Model):
    post_id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(to=Channel, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Channel, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"Post: {self.post_id}, author: {self.author}"


class PostComment(models.Model):
    author = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='post_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Channel, related_name='liked_post_comments', blank=True)

    def __str__(self):
        return f"Comment by {self.author}, post: {self.post}"
