from rest_framework import status

from core.apps.common.exceptions import ServiceException


class UserNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'User not found'}
