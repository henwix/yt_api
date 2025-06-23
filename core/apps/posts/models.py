import uuid

from django.db import models

from core.apps.channels.models import Channel
from core.apps.common.models import Comment


class Post(models.Model):
    post_id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(to=Channel, on_delete=models.CASCADE, related_name='posts', db_index=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Channel, through='PostLikeItem', blank=True)
    comments = models.ManyToManyField(Channel, through='PostCommentItems', related_name='posts_comments', blank=True)

    def __str__(self):
        return f'Post: {self.post_id}, author: {self.author_id}'


class PostLikeItem(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='liked_posts_items', db_index=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_items', db_index=True)
    is_like = models.BooleanField(default=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['channel', 'post'], name='unique_channel_post_like'),
        ]

    def __str__(self):
        return f'Like by {self.channel_id}, post {self.post_id}'


class PostCommentItems(Comment):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments_items', db_index=True)
    author = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='posts_comments_items', db_index=True)
    likes = models.ManyToManyField(
        Channel,
        through='PostCommentLikeItem',
        blank=True,
    )

    def __str__(self):
        return f'Comment by {self.author_id}, post: {self.post_id}'


class PostCommentLikeItem(models.Model):
    comment = models.ForeignKey(PostCommentItems, on_delete=models.CASCADE, related_name='likes_items', db_index=True)
    author = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='liked_posts_comments_items',
        db_index=True,
    )
    is_like = models.BooleanField(default=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'comment'], name='unique_post_comment_like'),
        ]

    def __str__(self):
        return f'Comment like by {self.author_id} to comment {self.comment_id}'
