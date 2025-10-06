import pytest
from pytest_django.fixtures import SettingsWrapper

from core.apps.users.use_cases.users.user_resend_activation import UserResendActivationUseCase
from core.tests.factories.channels import UserModelFactory


@pytest.mark.django_db
def test_user_resend_activation(
    settings: SettingsWrapper,
    user_resend_activation_use_case: UserResendActivationUseCase,
):
    settings.AUTH_SEND_ACTIVATION_EMAIL = True

    user = UserModelFactory.create(is_active=False)
    result = user_resend_activation_use_case.execute(email=user.email)
    assert result == {'detail': 'Activation email successfully sent'}
