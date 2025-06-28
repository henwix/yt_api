from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


@dataclass
class PostAuthorSlugNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': "to get Posts by author 'slug' you need to provide 's' query-parameter"}

    @property
    def message(self):
        return "'s' query-parameter to get Posts by author 'slug' was not provided"


@dataclass
class PostNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Post not found'}

    post_id: str | None = None

    @property
    def message(self):
        return 'Post not found'


@dataclass
class PostLikeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Post like not found'}

    channel_slug: str | None = None
    post_id: str | None = None

    @property
    def message(self):
        return 'Video like/dislike not found'
