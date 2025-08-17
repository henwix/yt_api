from logging import Logger

from rest_framework.permissions import BasePermission

import orjson
import punq

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.services.captcha import BaseCaptchaService
from core.project.containers import get_container


class CaptchaPermission(BasePermission):
    def has_permission(self, request, view):
        container: punq.Container = get_container()
        captcha_service: BaseCaptchaService = container.resolve(BaseCaptchaService)
        logger: Logger = container.resolve(Logger)

        try:
            return captcha_service.validate_token(
                token=request.data.get('captcha_token'),
                captcha_required=view.captcha_required,
                remoteip=request.META.get('HTTP_X_REAL_IP'),
            )

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise
