from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

import punq
import pytest

from core.apps.users.converters.users import (
    user_from_entity,
    user_to_entity,
)
from core.apps.users.exceptions.users import (
    UserNotFoundError,
    UserWithThisDataAlreadyExistsError,
)
from core.apps.users.models import CustomUser
from core.apps.users.services.users import (
    BaseUserService,
    BaseUserValidatorService,
)
from core.project.containers import get_container
from core.tests.factories.channels import UserModelFactory


User = get_user_model()


@pytest.mark.django_db
def test_user_authentication(user_service: BaseUserService):
    """Test that the user is authenticated and has been retrieved correctly."""

    password = '1234q1234q'
    user = UserModelFactory()
    user.set_password(password)
    user.save()

    authenticated_by_username = user_from_entity(
        user_service.authenticate(
            login=user.username,
            password=password,
        ),
    )
    authenticated_by_email = user_from_entity(
        user_service.authenticate(
            login=user.email,
            password=password,
        ),
    )

    assert user == authenticated_by_username
    assert user == authenticated_by_email


def test_user_not_found():
    """Test that an error has been raised when user is not found."""

    container: punq.Container = get_container()
    validator_service: BaseUserValidatorService = container.resolve(BaseUserValidatorService)

    with pytest.raises(UserNotFoundError):
        validator_service.validate(user=None)


@pytest.mark.django_db
def test_get_user_by_email(user_service: BaseUserService, user: User):
    """Test that the user has been retrieved by email from database."""

    user_dto = user_from_entity(user_service.get_by_email_or_404(user.email))

    assert user == user_dto


@pytest.mark.django_db
def test_jwt_generated_for_user(user_service: BaseUserService, client: APIClient, user: User):
    """Test that JWT token is correctly generated for user."""

    tokens = user_service.generate_jwt(user=user)
    client.credentials(HTTP_AUTHORIZATION=tokens.get('access'))

    access_response = client.post('/v1/token/verify/', {'token': tokens.get('access')})
    refresh_response = client.post('/v1/token/verify/', {'token': tokens.get('refresh')})

    assert access_response.status_code == 200
    assert refresh_response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_username, expected_email, expected_password',
    argvalues=(
        ['username_test', 'TestUsername', 'lkjhflh109234'],
        ['test_email@test.com', 'testtesttest@example.com', '123984842@gmail.com'],
        ['testpassword1283748124', 'ASfh1i1sf2h021', '9128479124asflkhasfASF'],
    ),
)
def test_user_created_by_data(
    user_service: BaseUserService,
    expected_username: str,
    expected_email: str,
    expected_password: str,
):
    """Test that user has been created by provided data."""

    result: CustomUser = user_service.create_by_data(
        data={
            'username': expected_username,
            'email': expected_email,
            'password': expected_password,
        },
    )

    database_user = CustomUser.objects.get(pk=result.pk)

    assert database_user.username == expected_username
    assert database_user.email == expected_email
    assert database_user.check_password(expected_password)


@pytest.mark.django_db
def test_user_username_exists_error(
    user_service: BaseUserService,
):
    """Test that an error has been raised when the user with this username
    already exists."""

    expected_username = 'username_test'
    expected_email = 'test_email@test.com'
    expected_password = 'PasswordTest_123456'

    UserModelFactory.create(username=expected_username)

    with pytest.raises(UserWithThisDataAlreadyExistsError):
        user_service.create_by_data(
            data={
                'username': expected_username,
                'email': expected_email,
                'password': expected_password,
            },
        )


@pytest.mark.django_db
def test_user_email_exists_error(
    user_service: BaseUserService,
):
    """Test that an error has been raised when the user with this email already
    exists."""

    expected_username = 'username_test'
    expected_email = 'test_email@test.com'
    expected_password = 'PasswordTest_123456'

    UserModelFactory.create(email=expected_email)

    with pytest.raises(UserWithThisDataAlreadyExistsError):
        user_service.create_by_data(
            data={
                'username': expected_username,
                'email': expected_email,
                'password': expected_password,
            },
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_new_password',
    argvalues=['1234q1234q', 'HelloWorldPassword1953', 'KJ19a012slffap1', 'Vao12Fas_(*!@&$'],
)
def test_password_updated(
    user_service: BaseUserService,
    user: CustomUser,
    expected_new_password: str,
):
    user_service.set_password(user=user_to_entity(user), password=expected_new_password)
    database_user = CustomUser.objects.get(username=user.username)

    assert database_user.check_password(expected_new_password)
