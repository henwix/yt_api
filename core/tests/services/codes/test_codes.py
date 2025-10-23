from django.core.cache import cache

import pytest

from core.apps.common.constants import CACHE_KEYS
from core.apps.users.converters.users import user_to_entity
from core.apps.users.exceptions.codes import (
    OtpCodeNotEqualError,
    OtpCodeNotFoundError,
    SetEmailCodeNotProvidedOrNotFoundError,
    SetEmailUserNotEqualError,
    UserEmailCodeNotEqualError,
    UserEmailCodeNotFoundError,
)
from core.apps.users.models import CustomUser
from core.apps.users.services.codes import BaseCodeService
from core.tests.factories.channels import UserModelFactory


@pytest.mark.django_db
def test_otp_code_generated_and_cached(code_service: BaseCodeService):
    """Test that the otp code has been generated and cached."""

    email = 'test@test.com'
    code = code_service.generate_email_otp_code(email)

    assert len(cache.keys('*')) == 1
    assert code is not None


@pytest.mark.django_db
def test_otp_code_validated(code_service: BaseCodeService):
    """Test that the otp code has been validated and cache deleted."""

    email = 'test@test.com'
    code = code_service.generate_email_otp_code(email)
    assert len(cache.keys('*')) == 1

    code_service.validate_email_otp_code(email, code)
    assert len(cache.keys('*')) == 0


@pytest.mark.django_db
def test_otp_code_not_provided_error(code_service: BaseCodeService):
    """Test that an error has been raised when the otp code is not provided."""

    email = 'test@test.com'

    with pytest.raises(OtpCodeNotFoundError):
        code_service.validate_email_otp_code(email, None)


@pytest.mark.django_db
def test_otp_code_not_equal_error(code_service: BaseCodeService):
    """Test that an error has been raised when the otp code is not equal."""

    email = 'test@test.com'
    code_service.generate_email_otp_code(email)

    with pytest.raises(OtpCodeNotEqualError):
        code_service.validate_email_otp_code(email, '123456')


@pytest.mark.django_db
def test_set_email_code_generated_and_cached(code_service: BaseCodeService, user: CustomUser):
    """Test that set_email code has been generated and cache is exists with
    correct data."""

    expected_new_email = 'new_test_email123456@test.com'

    code = code_service.generate_set_email_code(user_id=user.id, email=expected_new_email)
    cached_data_using_code = cache.get(CACHE_KEYS.get('set_email') + code)

    assert isinstance(code, str)
    assert len(code) == 32
    assert bool(cached_data_using_code)
    assert cached_data_using_code.get('new_email') == expected_new_email
    assert cached_data_using_code.get('user_id') == user.id


@pytest.mark.django_db
def test_set_email_code_validated(code_service: BaseCodeService, user: CustomUser):
    """Test that set_email code has been validated and code has been deleted
    from cache."""

    expected_new_email = 'new_test_email123456@test.com'

    code = code_service.generate_set_email_code(user_id=user.id, email=expected_new_email)
    assert len(cache.keys('*')) == 1

    email = code_service.validate_set_email_code(user_id=user.id, code=code)
    assert len(cache.keys('*')) == 0

    assert email == expected_new_email


@pytest.mark.django_db
def test_set_email_code_not_found_error_with_no_cache(code_service: BaseCodeService, user: CustomUser):
    """Test that an SetEmailCodeNotProvidedOrNotFoundError error has been
    raised when the cache is not exists."""

    with pytest.raises(SetEmailCodeNotProvidedOrNotFoundError):
        code_service.validate_set_email_code(user_id=user.id, code='test_code')


@pytest.mark.django_db
def test_set_email_code_not_found_error_with_cache(code_service: BaseCodeService, user: CustomUser):
    """Test that an SetEmailCodeNotProvidedOrNotFoundError error has been
    raised when the cache is exists."""

    code_service.generate_set_email_code(user_id=user.id, email='new_test_email123456@test.com')

    with pytest.raises(SetEmailCodeNotProvidedOrNotFoundError):
        code_service.validate_set_email_code(user_id=user.id, code='test_code')


@pytest.mark.django_db
def test_set_email_code_user_id_not_equal_error(code_service: BaseCodeService, user: CustomUser):
    """Test that an SetEmailUserNotEqualError error has been raised."""

    code = code_service.generate_set_email_code(user_id=user.id, email='test_email@test.com')

    with pytest.raises(SetEmailUserNotEqualError):
        code_service.validate_set_email_code(user_id=666111333222, code=code)


@pytest.mark.django_db
def test_user_email_code_generated_and_cached(code_service: BaseCodeService, user: CustomUser):
    """Test that user code has been generated and cached."""

    cache_prefix = 'test_user_email_code_prefix_'

    code = code_service.generate_user_email_code(user=user_to_entity(user), cache_prefix=cache_prefix)
    cached_code = cache.get(f'{cache_prefix}{user.pk}')

    assert isinstance(code, str)
    assert len(code) == 32
    assert code == cached_code


@pytest.mark.django_db
def test_user_email_code_validated(code_service: BaseCodeService, user: CustomUser):
    """Test that the user_email_code has been validated and deleted from
    cache."""

    cache_prefix = 'test_user_email_code_prefix_'
    code = code_service.generate_user_email_code(user=user_to_entity(user), cache_prefix=cache_prefix)
    assert len(cache.keys('*')) == 1

    result = code_service.validate_user_email_code(user=user_to_entity(user), code=code, cache_prefix=cache_prefix)
    assert len(cache.keys('*')) == 0
    assert result


@pytest.mark.django_db
def test_user_email_code_not_found_with_code_for_other_user(code_service: BaseCodeService):
    """Test that an error UserEmailCodeNotFoundError has been raised when the
    code is generated for other user."""

    cache_prefix = 'test_user_email_code_prefix_'
    user_with_code = UserModelFactory.create()
    user_without_code = UserModelFactory.create()
    code = code_service.generate_user_email_code(user=user_to_entity(user_with_code), cache_prefix=cache_prefix)

    with pytest.raises(UserEmailCodeNotFoundError):
        code_service.validate_user_email_code(
            user=user_to_entity(user_without_code),
            code=code,
            cache_prefix=cache_prefix,
        )


@pytest.mark.django_db
def test_user_email_code_not_found_without_code(code_service: BaseCodeService, user: CustomUser):
    """Test that an error UserEmailCodeNotFoundError has been raised when the
    code is not generated."""

    cache_prefix = 'test_user_email_code_prefix_'

    with pytest.raises(UserEmailCodeNotFoundError):
        code_service.validate_user_email_code(
            user=user_to_entity(user),
            code='test_code',
            cache_prefix=cache_prefix,
        )


@pytest.mark.django_db
def test_user_email_code_not_equal_error(code_service: BaseCodeService, user: CustomUser):
    """Test that an error UserEmailCodeNotEqualError has been raised."""

    cache_prefix = 'test_user_email_code_prefix_'
    code_service.generate_user_email_code(user=user_to_entity(user), cache_prefix=cache_prefix)

    with pytest.raises(UserEmailCodeNotEqualError):
        code_service.validate_user_email_code(user=user_to_entity(user), code='test_code', cache_prefix=cache_prefix)
