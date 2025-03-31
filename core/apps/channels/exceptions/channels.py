from dataclasses import dataclass

from rest_framework import status

from apps.common.exceptions import ServiceException


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


@dataclass
class SelfSubscriptionError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': "You can't subscribe to yourself"}

    channel_slug: str

    @property
    def message(self):
        return f"User can't subscribe to himself: {self.channel_slug}"


@dataclass
class SubscriptionExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Subscription already exists'}

    sub_slug: str
    sub_to_slug: str

    @property
    def message(self):
        return f'{self.sub_slug} already subscribed to {self.sub_to_slug}'


@dataclass
class SubscriptionDoesNotExistsError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Subscription does not exists'}

    sub_slug: str
    sub_to_slug: str

    @property
    def message(self):
        return f'Subscription {self.sub_slug} to {self.sub_to_slug} does not exists'
