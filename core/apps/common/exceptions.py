from dataclasses import dataclass

from rest_framework import status
from rest_framework.exceptions import APIException


@dataclass
class ServiceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Application exception occurred'}

    def __post_init__(self):
        super().__init__()

    @property
    def message(self):
        return 'Application exception occurred'
