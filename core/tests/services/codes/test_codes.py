from django.core.cache import cache
from django.db.utils import settings

import pytest

from core.apps.users.exceptions.codes import (
    OtpCodeNotEqualError,
    OtpCodeNotProvidedOrNotFoundError,
    SetEmailCodeNotProvidedOrNotFoundError,
    SetEmailUserNotEqualError,
)
from core.apps.users.models import CustomUser
from core.apps.users.services.codes import BaseCodeService


@pytest.mark.django_db
def test_code_generated(code_service: BaseCodeService):
    """Test that the code has been generated."""

    email = 'test@test.com'
    code = code_service.generate_email_otp_code(email)

    assert code is not None


@pytest.mark.django_db
def test_code_validated(code_service: BaseCodeService):
    """Test that the code has been validated."""

    email = 'test@test.com'
    code = code_service.generate_email_otp_code(email)

    code_service.validate_email_otp_code(email, code)


@pytest.mark.django_db
def test_code_not_provided_error(code_service: BaseCodeService):
    """Test that an error has been raised when the code is not provided."""

    email = 'test@test.com'

    with pytest.raises(OtpCodeNotProvidedOrNotFoundError):
        code_service.validate_email_otp_code(email, None)


@pytest.mark.django_db
def test_code_not_equal_error(code_service: BaseCodeService):
    """Test that an error has been raised when the code is not equal."""

    email = 'test@test.com'
    code_service.generate_email_otp_code(email)

    with pytest.raises(OtpCodeNotEqualError):
        code_service.validate_email_otp_code(email, '123456')


@pytest.mark.django_db
def test_set_email_code_generated(code_service: BaseCodeService, user: CustomUser):
    """Test that set_email code has been generated."""

    expected_new_email = 'new_test_email@test.com'

    code = code_service.generate_set_email_code(user_id=user.id, email=expected_new_email)

    assert isinstance(code, str)
    assert len(code) == 32


@pytest.mark.django_db
def test_set_email_code_generated_and_cached(code_service: BaseCodeService, user: CustomUser):
    """Test that set_email code has been generated and cache is exists with
    correct data."""

    expected_new_email = 'new_test_email123456@test.com'

    code = code_service.generate_set_email_code(user_id=user.id, email=expected_new_email)
    cached_data_using_code = cache.get(settings.CACHE_KEYS.get('set_email') + code)

    assert isinstance(code, str)
    assert len(code) == 32
    assert bool(cached_data_using_code)
    assert cached_data_using_code.get('new_email') == expected_new_email
    assert cached_data_using_code.get('user_id') == user.id


@pytest.mark.django_db
def test_set_email_code_validated(code_service: BaseCodeService, user: CustomUser):
    """Test that set_email code has been validated."""

    expected_new_email = 'new_test_email123456@test.com'

    code = code_service.generate_set_email_code(user_id=user.id, email=expected_new_email)
    email = code_service.validate_set_email_code(user_id=user.id, code=code)

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
