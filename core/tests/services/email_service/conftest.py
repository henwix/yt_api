import punq
import pytest

from core.apps.common.services.smtp_email import BaseEmailService


@pytest.fixture
def email_service(container: punq.Container) -> BaseEmailService:
    return container.resolve(BaseEmailService)
