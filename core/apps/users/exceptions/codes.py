from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


class CodeNotFoundException(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Code not found'}

    @property
    def message(self):
        return f'Code {self.code} not found'


@dataclass
class CodeNotEqualException(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Code not equal'}

    cached_code: str
    user_code: str

    @property
    def message(self):
        return f'Code {self.cached_code} not equal {self.user_code}'
