from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class SelfSubscriptionError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': "You can't subscribe/unsubscribe to/from yourself"}

    channel_slug: str


@dataclass
class SubscriptionExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Subscription already exists'}

    sub_slug: str
    sub_to_slug: str


@dataclass
class SubscriptionDoesNotExistError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Subscription does not exist'}

    sub_slug: str
    sub_to_slug: str
