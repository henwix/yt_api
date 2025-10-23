from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class ChannelNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Channel not found'}

    user_id: int | str


@dataclass
class ChannelWithSlugNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Channel with this slug is not found'}

    channel_slug: str


@dataclass
class AvatarDoesNotExistError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Avatar does not exist'}

    channel_slug: str


@dataclass
class ChannelSlugInvalidValueError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Channel slug invalid value'}

    slug: str
