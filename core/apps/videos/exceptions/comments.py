from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


class CommentNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Comment not found'}

    @property
    def message(self):
        return 'Comment not found'


@dataclass
class CommentLikeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Comment like/dislike not found'}

    channel_slug: str
    comment_id: int

    @property
    def message(self):
        return f'Like/dislike by channel {self.channel_slug} not found for comment {self.comment_id}'
