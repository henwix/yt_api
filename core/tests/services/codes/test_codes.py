import pytest

from core.apps.users.exceptions.codes import (
    OtpCodeNotEqualError,
    OtpCodeNotProvidedOrNotFoundError,
)
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
