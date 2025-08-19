from django.conf import settings

from core.apps.common.exceptions.captcha import CaptchaVersionNotSupported


def get_captcha_service_fabric(version: str):
    services = settings.CAPTCHA_VERSION_SERVICES
    service = services.get(version)

    if not service:
        raise CaptchaVersionNotSupported(version=version)

    return service
