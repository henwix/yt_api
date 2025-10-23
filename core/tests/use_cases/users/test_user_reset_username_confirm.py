import pytest

from core.apps.common.constants import CACHE_KEYS
from core.apps.common.services.encoding import BaseEncodingService
from core.apps.users.converters.users import user_to_entity
from core.apps.users.exceptions.users import InvalidUIDValueError
from core.apps.users.models import CustomUser
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.use_cases.users.user_reset_username_confirm import UserResetUsernameConfirmUseCase


@pytest.mark.django_db
@pytest.mark.parametrize('expected_username', ['TestNewUsername_123', 'asfakljfhka@tSA123', 'username_test'])
def test_user_reset_username_confirmed(
    expected_username: str,
    user_reset_username_confirm_use_case: UserResetUsernameConfirmUseCase,
    code_service: BaseCodeService,
    encoding_service: BaseEncodingService,
    user: CustomUser,
):
    """Test that username has been reset successfully."""

    code = code_service.generate_user_email_code(
        user=user_to_entity(user),
        cache_prefix=CACHE_KEYS.get('username_reset'),
    )
    encoded_id = encoding_service.base64_encode(data=user.pk)

    assert CustomUser.objects.filter(pk=user.pk, username=user.username).exists()
    assert not CustomUser.objects.filter(pk=user.pk, username=expected_username).exists()

    result = user_reset_username_confirm_use_case.execute(
        encoded_id=encoded_id,
        code=code,
        new_username=expected_username,
    )

    assert isinstance(result, dict)
    assert result == {'detail': 'Success'}
    assert not CustomUser.objects.filter(pk=user.pk, username=user.username).exists()
    assert CustomUser.objects.filter(pk=user.pk, username=expected_username).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('expected_uid', ["$$$", "abc", "abc===", "abcd1", "ab*c", '!!!', '10dj102jdasd', 'ASJBV'])
def test_user_reset_username_confirm_invalid_uid_error(
    expected_uid: str,
    user_reset_username_confirm_use_case: UserResetUsernameConfirmUseCase,
):
    """Test that an error InvalidUIDValueError has been raised when the UID
    value is ivalid."""

    with pytest.raises(InvalidUIDValueError):
        user_reset_username_confirm_use_case.execute(encoded_id=expected_uid, code='test_code', new_username='123')
