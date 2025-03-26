from rest_framework import status

from apps.common.exceptions import ServiceException


class VideoNotFound(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Video not found'}

    @property
    def message(self):
        return 'Video not found'


class LikeNotFound(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Like not found'}

    @property
    def message(self):
        return 'Like not found'


class ViewExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'View already exists. You can add 1 view per 24h.'}

    @property
    def message(self):
        return 'View already exists'
