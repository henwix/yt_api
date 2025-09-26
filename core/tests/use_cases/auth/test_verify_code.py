import pytest

from core.apps.users.services.codes import BaseCodeService
from core.apps.users.use_cases.users.auth_verify_code import VerifyCodeUseCase
from core.tests.factories.channels import UserModelFactory


@pytest.mark.django_db
def test_code_verified(verify_code_use_case: VerifyCodeUseCase, code_service: BaseCodeService):
    """Test that the code has been verified and jwt tokens have been
    generated."""

    expected_email = 'test_email@test.com'
    UserModelFactory.create(email=expected_email)
    expected_code = code_service.generate_email_otp_code(email=expected_email)

    result = verify_code_use_case.execute(email=expected_email, code=expected_code)

    assert type(result) is dict
    assert result.get('access') is not None
    assert result.get('refresh') is not None
