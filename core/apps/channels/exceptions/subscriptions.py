from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class SelfSubscriptionError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': "you can't subscribe/unsubscribe to/from yourself"}

    channel_slug: str

    @property
    def message(self):
        return "User can't subscribe/unsubscribe to/from yourself"


@dataclass
class SubscriptionExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'subscription already exists'}

    sub_slug: str
    sub_to_slug: str

    @property
    def message(self):
        return 'Subscription already exists'


@dataclass
class SubscriptionDoesNotExistsError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'subscription does not exists'}

    sub_slug: str
    sub_to_slug: str

    @property
    def message(self):
        return 'Subscription does not exists'
