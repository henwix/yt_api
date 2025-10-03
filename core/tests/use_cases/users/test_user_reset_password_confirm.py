from django.db.utils import settings

import pytest

from core.apps.common.services.encoding import BaseEncodingService
from core.apps.users.converters.users import user_to_entity
from core.apps.users.exceptions.users import InvalidUIDValueError
from core.apps.users.models import CustomUser
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.use_cases.users.user_reset_password_confirm import UserResetPasswordConfirmUseCase


@pytest.mark.django_db
@pytest.mark.parametrize('expected_password', ['Test_New_password_123_456', 'asfkgaoi1u2fb', '1111000222jjjjasF'])
def test_user_reset_password_confirmed(
    expected_password: str,
    user_reset_password_confirm_use_case: UserResetPasswordConfirmUseCase,
    code_service: BaseCodeService,
    encoding_service: BaseEncodingService,
    user: CustomUser,
):
    """Test that password has been reset successfully."""

    code = code_service.generate_user_email_code(
        user=user_to_entity(user),
        cache_prefix=settings.CACHE_KEYS.get('password_reset'),
    )
    encoded_id = encoding_service.base64_encode(data=user.pk)

    result = user_reset_password_confirm_use_case.execute(
        encoded_id=encoded_id,
        code=code,
        new_password=expected_password,
    )

    assert isinstance(result, dict)
    assert result == {'detail': 'Success'}
    assert CustomUser.objects.get(pk=user.pk).check_password(expected_password)


@pytest.mark.django_db
@pytest.mark.parametrize('expected_uid', ["$$$", "abc", "abc===", "abcd1", "ab*c", '!!!', '10dj102jdasd', 'ASJBV'])
def test_user_reset_password_confirm_invalid_uid_error(
    expected_uid: str,
    user_reset_password_confirm_use_case: UserResetPasswordConfirmUseCase,
):
    """Test that an error InvalidUIDValueError has been raised when the UID
    value is ivalid."""

    with pytest.raises(InvalidUIDValueError):
        user_reset_password_confirm_use_case.execute(encoded_id=expected_uid, code='test_code', new_password='123')
