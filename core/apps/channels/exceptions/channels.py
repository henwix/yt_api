from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class ChannelNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Channel not found'}

    user_id: int | str

    @property
    def message(self):
        return 'Channel is not found'


@dataclass
class SlugChannelNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Channel with this slug is not found'}

    channel_slug: str

    @property
    def message(self):
        return 'Channel with this slug is not found'


@dataclass
class AvatarDoesNotExistsError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Avatar does not exists'}

    channel_slug: str

    @property
    def message(self):
        return 'Avatar does not exists'
