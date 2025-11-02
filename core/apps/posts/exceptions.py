from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class PostAuthorSlugNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': "'s' query-parameter was not provided"}


@dataclass
class PostNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Post not found'}

    post_id: str | None = None


@dataclass
class PostLikeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Post like not found'}

    channel_slug: str | None = None
    post_id: str | None = None


@dataclass
class PostSubscriptionTierLimitError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'You have reached the maximum number of posts'}

    user_id: int
    limit: int
    current_posts_number: int
