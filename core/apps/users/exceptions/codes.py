from rest_framework import status

from apps.common.exceptions import ServiceException


class CodeNotFoundException(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Code not found'}

    @property
    def message(self):
        return 'Code not found'


class CodeNotEqualException(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Code not equal'}

    @property
    def message(self):
        return 'Code not equal'
