import pytest

from core.apps.users.models import CustomUser
from core.apps.users.use_cases.users.user_reset_password import UserResetPasswordUseCase


@pytest.mark.django_db
def test_user_reset_password_email_sent(user_reset_password_use_case: UserResetPasswordUseCase, user: CustomUser):
    result = user_reset_password_use_case.execute(email=user.email)

    assert isinstance(result, dict)
    assert result == {'detail': 'Confirmation email successfully sent'}
