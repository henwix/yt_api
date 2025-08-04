from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class CommentNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Comment not found'}

    @property
    def message(self):
        return 'Comment is not found'


@dataclass
class CommentLikeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Comment like or dislike not found'}

    channel_slug: str
    comment_id: int

    @property
    def message(self):
        return 'Comment like or dislike was not found'
