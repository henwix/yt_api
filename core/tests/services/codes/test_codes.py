import pytest

from core.apps.users.exceptions.codes import (
    CodeNotEqualException,
    CodeNotProvidedException,
)
from core.apps.users.services.codes import BaseCodeService


@pytest.mark.django_db
def test_code_generated(code_service: BaseCodeService):
    """Test code generated."""
    email = 'test@test.com'
    code = code_service.generate_code(email)

    assert code is not None


@pytest.mark.django_db
def test_code_validated(code_service: BaseCodeService):
    """Test code validated."""
    email = 'test@test.com'
    code = code_service.generate_code(email)

    code_service.validate_code(email, code)


@pytest.mark.django_db
def test_code_not_provided_error(code_service: BaseCodeService):
    """Test error raised when code not provided."""
    email = 'test@test.com'

    with pytest.raises(CodeNotProvidedException):
        code_service.validate_code(email, None)


@pytest.mark.django_db
def test_code_not_equal_error(code_service: BaseCodeService):
    """Test error raised when code is not equal."""
    email = 'test@test.com'
    code_service.generate_code(email)

    with pytest.raises(CodeNotEqualException):
        code_service.validate_code(email, '123456')
