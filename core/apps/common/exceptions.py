from rest_framework.exceptions import APIException
from rest_framework import status


class ServiceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'Application exception occurred'}

    @property
    def message(self):
        return 'Application exception occurred'
