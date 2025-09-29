import pytest

from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser
from core.apps.users.use_cases.users.user_set_password import UserSetPasswordUseCase


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_new_password',
    argvalues=['1234q1234q15125', 'sdglsdg@$1Password1953', 'Aaaas1g2slffap1', '9#1!523GFas_(!@&$'],
)
def test_use_case_password_updated(
    user_set_password_use_case: UserSetPasswordUseCase,
    user: CustomUser,
    expected_new_password: str,
):
    user_set_password_use_case.execute(user=user_to_entity(user), password=expected_new_password)
    database_user = CustomUser.objects.get(username=user.username)

    assert database_user.check_password(expected_new_password)
