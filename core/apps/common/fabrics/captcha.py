from django.conf import settings

from core.apps.common.exceptions.captcha import CaptchaVersionNotSupportedError


def get_captcha_service_fabric(version: str) -> str:
    """Fabric function for captcha services.

    Args:
        version (str): Captcha version

    Raises:
        CaptchaVersionNotSupported: If the provided version is not supported

    Returns:
        str: Service class name to resolve it in Punq container

    """

    services = settings.CAPTCHA_VERSION_SERVICES
    service = services.get(version)

    if not service:
        raise CaptchaVersionNotSupportedError(version=version)

    return service
