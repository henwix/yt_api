import pytest

from core.apps.users.models import CustomUser
from core.apps.users.use_cases.users.user_reset_username import UserResetUsernameUseCase


@pytest.mark.django_db
def test_user_reset_username_email_sent(user_reset_username_use_case: UserResetUsernameUseCase, user: CustomUser):
    result = user_reset_username_use_case.execute(email=user.email)

    assert isinstance(result, dict)
    assert result == {'detail': 'Confirmation email successfully sent'}
