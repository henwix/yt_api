from logging import Logger

from django.conf import settings
from rest_framework.permissions import BasePermission

import orjson
import punq

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.fabrics.captcha import get_captcha_service_fabric
from core.apps.common.services.captcha import BaseCaptchaService
from core.project.containers import get_container


class CaptchaPermission(BasePermission):
    """Permission to validate captcha token. *Captcha is not required for
    superuser*.

    To activate this permission, set the attribute `captcha_allowed_methods` in the view class.

    The 'captcha_allowed_methods' is a list that may contain 'actions' from DRF viewsets and any HTTP methods.

    By default, if the attribute is not set, all requests will be allowed and captcha will not be validated.

    """

    def has_permission(self, request, view):
        if 'test_captcha' in request.data.keys() and settings.DEBUG or not settings.CAPTCHA_VALIDATION_ENABLED:
            return True

        methods = getattr(view, 'captcha_allowed_methods', [])  # get list of allowed methods for captcha

        if request.method in methods or getattr(view, 'action', None) in methods:
            container: punq.Container = get_container()
            captcha_service: BaseCaptchaService = container.resolve(
                get_captcha_service_fabric(request.data.get('captcha_version')),
            )
            logger: Logger = container.resolve(Logger)

            logger.info(
                msg='Service for captcha has been resolved',
                extra={
                    'log_meta': orjson.dumps({
                        'version': request.data.get('captcha_version'),
                        'service': captcha_service.__class__.__name__,
                    }).decode(),
                },
            )

            try:
                return captcha_service.validate_token(
                    version=request.data.get('captcha_version'),
                    token=request.data.get('captcha_token'),
                    remoteip=request.META.get('HTTP_X_REAL_IP'),
                )

            except ServiceException as error:
                logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
                raise

        return True
