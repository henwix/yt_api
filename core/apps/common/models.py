from django.db import models


class Comment(models.Model):
    reply_level_choices = [
        (0, 0),
        (1, 1),
    ]

    id = models.BigAutoField(primary_key=True, unique=True, editable=False, db_index=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_updated = models.BooleanField(default=False)
    reply_comment = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        help_text='Comment to reply',
    )
    reply_level = models.PositiveIntegerField(choices=reply_level_choices, default=0, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'Comment #{id}'
