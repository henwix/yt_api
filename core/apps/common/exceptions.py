from rest_framework import status
from rest_framework.exceptions import APIException


class ServiceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Application exception occurred'}

    @property
    def message(self):
        return 'Application exception occurred'
