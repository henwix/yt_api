import pytest
from pytest_django.fixtures import SettingsWrapper

from core.apps.common.constants import CACHE_KEYS
from core.apps.common.services.encoding import BaseEncodingService
from core.apps.users.converters.users import user_to_entity
from core.apps.users.exceptions.users import InvalidUIDValueError
from core.apps.users.models import CustomUser
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.use_cases.users.user_activation import UserActivationUseCase
from core.tests.factories.channels import UserModelFactory


@pytest.mark.django_db
def test_user_activated(
    settings: SettingsWrapper,
    user_activation_use_case: UserActivationUseCase,
    code_service: BaseCodeService,
    encoding_service: BaseEncodingService,
):
    settings.AUTH_SEND_ACTIVATION_EMAIL = True

    user = UserModelFactory.create(is_active=False)

    code = code_service.generate_user_email_code(
        user=user_to_entity(user),
        cache_prefix=CACHE_KEYS.get('activate_user'),
    )
    encoded_id = encoding_service.base64_encode(data=user.pk)

    assert not CustomUser.objects.filter(pk=user.pk, is_active=True).exists()

    result = user_activation_use_case.execute(encoded_id=encoded_id, code=code)

    assert CustomUser.objects.filter(pk=user.pk, is_active=True).exists()
    assert result == {'detail': 'Success'}


@pytest.mark.django_db
@pytest.mark.parametrize('expected_uid', ['$$$', 'abc', 'abc===', 'abcd1', 'ab*c', '!!!', '10dj102jdasd', 'ASJBV'])
def test_user_activation_invalid_uid_error(
    settings: SettingsWrapper,
    expected_uid: str,
    user_activation_use_case: UserActivationUseCase,
):
    """Test that an error InvalidUIDValueError has been raised when the UID
    value is ivalid."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = True

    with pytest.raises(InvalidUIDValueError):
        user_activation_use_case.execute(encoded_id=expected_uid, code='test_code')
