import pytest

from core.apps.users.exceptions.users import UserNotFoundError
from core.apps.users.models import CustomUser
from core.apps.users.use_cases.auth import AuthorizeUserUseCase


@pytest.mark.django_db
def test_auth_user_jwt_retrieved_by_username(authorize_user_use_case: AuthorizeUserUseCase):
    """Test that the user is authorized and tokens are retrieved by username
    and password."""

    expected_username = 'TestUsername123'
    expected_password = 'TestPassword456'
    expected_email = 'TestEmail789@gmail.com'

    CustomUser.objects.create_user(email=expected_email, password=expected_password, username=expected_username)

    tokens = authorize_user_use_case.execute(
        login=expected_username,
        password=expected_password,
    )

    assert type(tokens) is dict
    assert tokens.get('access') is not None
    assert tokens.get('refresh') is not None


@pytest.mark.django_db
def test_auth_user_jwt_retrieved_by_email(authorize_user_use_case: AuthorizeUserUseCase):
    """Test that the user is authorized and tokens are retrieved by email and
    password."""

    expected_username = 'TestUsername123'
    expected_password = 'TestPassword456'
    expected_email = 'TestEmail789@gmail.com'

    CustomUser.objects.create_user(email=expected_email, password=expected_password, username=expected_username)

    tokens = authorize_user_use_case.execute(
        login=expected_email,
        password=expected_password,
    )

    assert type(tokens) is dict
    assert tokens.get('access') is not None
    assert tokens.get('refresh') is not None


@pytest.mark.django_db
def test_auth_user_not_found_error(authorize_user_use_case: AuthorizeUserUseCase):
    """Test that an error is raised when the user is not found."""

    expected_username = 'TestUsername123'
    expected_password = 'TestPassword456'

    with pytest.raises(UserNotFoundError):
        authorize_user_use_case.execute(
            login=expected_username,
            password=expected_password,
        )


@pytest.mark.django_db
def test_auth_user_email_sent_with_enabled_otp(authorize_user_use_case: AuthorizeUserUseCase):
    """Test that an email is sent when the user is authorized and has enabled
    otp."""

    expected_username = 'TestUsername123'
    expected_password = 'TestPassword456'
    expected_email = 'TestEmail789@gmail.com'

    CustomUser.objects.create_user(
        email=expected_email,
        password=expected_password,
        username=expected_username,
        otp_enabled=True,
    )

    result = authorize_user_use_case.execute(
        login=expected_email,
        password=expected_password,
    )

    assert type(result) is dict
    assert result.get('detail') == 'Email successfully sent'
