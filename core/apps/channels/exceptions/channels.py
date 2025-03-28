from rest_framework import status

from apps.common.exceptions import ServiceException


class ChannelNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Channel not found'}

    @property
    def message(self):
        return 'Channel not found for user'


class AvatarExceptionError(ServiceException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = {'error': 'Something went wrong with avatar removing'}

    @property
    def message(self):
        return 'Something went wrong with avatar removing for channel'


class AvatarDoesNotExistsError(AvatarExceptionError):
    # FIXME: ошибка при попытке удаления аватарки через swagger: web-1  | AttributeError: 'AvatarDoesNotExists' object has no attribute 'detail'. Это из-за датакласса, чек в Chatgpt
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Avatar does not exists'}

    @property
    def message(self):
        return 'Avatar does not exists for channel'


class SelfSubscriptionError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'You cannot subscribe to yourself'}

    @property
    def message(self):
        return 'You cannot subscribe to yourself'


class SubscriptionExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Subscription already exists'}

    @property
    def message(self):
        return 'Subscription already exists'


class SubscriptionDoesNotExistsError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Subscription does not exists'}

    @property
    def message(self):
        return 'Subscription does not exists'
