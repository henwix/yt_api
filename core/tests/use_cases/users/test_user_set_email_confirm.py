import pytest

from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.use_cases.users.user_set_email_confirm import UserSetEmailConfirmUseCase


@pytest.mark.django_db
def test_set_email_confirmed(
    user_set_email_confirm_use_case: UserSetEmailConfirmUseCase,
    code_service: BaseCodeService,
    user: CustomUser,
):
    expected_email = '123321test_set_email@test.com'
    generated_code = code_service.generate_set_email_code(
        user_id=user.pk,
        email=expected_email,
    )

    assert not CustomUser.objects.filter(pk=user.pk, email=expected_email).exists()
    assert CustomUser.objects.filter(pk=user.pk, email=user.email).exists()

    result = user_set_email_confirm_use_case.execute(user=user_to_entity(user), code=generated_code)

    assert isinstance(result, dict)
    assert result['detail'] == 'Success'
    assert result['new_email'] == expected_email
    assert CustomUser.objects.filter(pk=user.pk, email=expected_email).exists()
    assert not CustomUser.objects.filter(pk=user.pk, email=user.email).exists()
