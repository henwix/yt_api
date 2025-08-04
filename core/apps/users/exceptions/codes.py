from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class CodeNotProvidedException(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Code not provided'}

    email: str

    @property
    def message(self):
        return 'Code is not provided'


@dataclass
class CodeNotEqualException(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Code not equal'}

    cached_code: str
    user_code: str

    @property
    def message(self):
        return 'Code is not equal'
