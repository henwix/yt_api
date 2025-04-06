from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


@dataclass
class ChannelNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Channel not found'}

    user_id: int

    @property
    def message(self):
        return f'Channel not found for user: {self.user_id}'


@dataclass
class AvatarExceptionError(ServiceException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = {'error': 'Something went wrong with avatar removing'}

    channel_slug: str

    @property
    def message(self):
        return f'Something went wrong with avatar removing for channel {self.channel_slug}'


@dataclass
class AvatarDoesNotExistsError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Avatar does not exists'}

    channel_slug: str

    @property
    def message(self):
        return f'Avatar does not exists for channel {self.channel_slug}'
