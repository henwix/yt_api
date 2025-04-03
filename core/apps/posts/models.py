import uuid

from django.db import models

from core.apps.channels.models import Channel


class Post(models.Model):
    post_id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(to=Channel, on_delete=models.CASCADE, related_name='posts', db_index=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Channel, related_name='liked_posts', blank=True)

    def __str__(self):
        return f'Post: {self.post_id}, author: {self.author}'


class PostComment(models.Model):
    author = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='post_comments', db_index=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', db_index=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Channel, related_name='liked_post_comments', blank=True)

    def __str__(self):
        return f'Comment by {self.author}, post: {self.post}'
