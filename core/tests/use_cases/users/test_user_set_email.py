import pytest

from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser
from core.apps.users.use_cases.users.user_set_email import UserSetEmailUseCase


@pytest.mark.django_db
def test_set_email_confirmation_sent(
    user_set_email_use_case: UserSetEmailUseCase,
    user: CustomUser,
):
    result: dict = user_set_email_use_case.execute(user=user_to_entity(user), email='test_email@test.com')
    assert result == {'detail': 'Confirmation email successfully sent'}
