from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

import punq
import pytest
from pytest_django.fixtures import SettingsWrapper

from core.apps.users.converters.users import (
    user_from_entity,
    user_to_entity,
)
from core.apps.users.exceptions.users import (
    UserActivationNotAllowedError,
    UserAlreadyActivatedError,
    UserNotFoundError,
    UserWithThisDataAlreadyExistsError,
)
from core.apps.users.models import CustomUser
from core.apps.users.services.users import (
    BaseUserActivatedValidatorService,
    BaseUserActivationRequiredValidatorService,
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
def test_get_user_by_email_404_error(user_service: BaseUserService):
    """Test that an error has been raised when the user is not found by
    email."""

    with pytest.raises(UserNotFoundError):
        user_service.get_by_email_or_404(email='test')


@pytest.mark.django_db
def test_get_user_by_id(user_service: BaseUserService, user: User):
    """Test that the user has been retrieved by id from database."""

    user_dto = user_from_entity(user_service.get_by_id_or_404(user_id=user.pk))
    assert user == user_dto


@pytest.mark.django_db
def test_get_user_by_id_404_error(user_service: BaseUserService):
    """Test that an error has been raised when the user is not found by id."""

    with pytest.raises(UserNotFoundError):
        user_service.get_by_id_or_404(user_id=999)


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
        ['username_test', 'test_email@test.com', 'testpassword1283748124'],
        ['TestUsername', 'testtesttest@example.com', 'ASfh1i1sf2h021'],
        ['lkjhflh109234', '123984842@gmail.com', '9128479124asflkhasfASF'],
    ),

)
def test_user_created_by_data(
    user_service: BaseUserService,
    expected_username: str,
    expected_email: str,
    expected_password: str,
):
    """Test that user has been created by provided data."""

    created_user: CustomUser = user_service.create_by_data(
        data={
            'username': expected_username,
            'email': expected_email,
            'password': expected_password,
        },
    )

    database_user = CustomUser.objects.get(pk=created_user.pk)

    assert database_user.username == expected_username
    assert database_user.email == expected_email
    assert database_user.check_password(expected_password)
    assert not database_user.otp_enabled

    assert created_user.username == expected_username
    assert created_user.email == expected_email
    assert created_user.check_password(expected_password)
    assert not created_user.otp_enabled


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
    """Test that the password has been updated."""

    user_service.set_password(user=user_to_entity(user), password=expected_new_password)
    database_user = CustomUser.objects.get(username=user.username)

    assert database_user.check_password(expected_new_password)


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_username, expected_email, expected_otp_enabled',
    argvalues=[
        ('new_test_username', 'new_test_email@test.dev', True),
        ('UsernameNewTest', 'ajfhaksjf@example.com', False),
        ('123_567_user_name_new_test_123', 'example_email@example.com', True),
    ],
)
def test_user_data_updated(
    user_service: BaseUserService,
    user: CustomUser,
    expected_username: str,
    expected_email: str,
    expected_otp_enabled: bool,
):
    """Test that user data has been updated successfully."""

    user_service.update_by_data(
        user=user_to_entity(user), data={
            'username': expected_username,
            'email': expected_email,
            'otp_enabled': expected_otp_enabled,
        },
    )

    assert CustomUser.objects.filter(
        pk=user.pk,
        username=expected_username,
        email=expected_email,
        otp_enabled=expected_otp_enabled,
    ).exists()


@pytest.mark.django_db
def test_user_activation_validator_allowed(
    settings: SettingsWrapper,
    user_activation_required_validator_service: BaseUserActivationRequiredValidatorService,
):
    """Test that AUTH_SEND_ACTIVATION_EMAIL is allowed."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = True
    user_activation_required_validator_service.validate()


@pytest.mark.django_db
def test_user_activation_validator_not_allowed_error(
    settings: SettingsWrapper,
    user_activation_required_validator_service: BaseUserActivationRequiredValidatorService,
):
    """Test that AUTH_SEND_ACTIVATION_EMAIL is not allowed and an error has
    been raised."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = False

    with pytest.raises(UserActivationNotAllowedError):
        user_activation_required_validator_service.validate()


@pytest.mark.django_db
def test_user_activated_validator(user_activated_validator_service: BaseUserActivatedValidatorService):
    """Test that user is not activated and an error has not been raised."""

    user = UserModelFactory.create(is_active=False)
    user_activated_validator_service.validate(user=user_to_entity(user))


@pytest.mark.django_db
def test_user_activated_validator_error(user_activated_validator_service: BaseUserActivatedValidatorService):
    """Test that user is already activated and an error has been raised."""

    user = UserModelFactory.create(is_active=True)

    with pytest.raises(UserAlreadyActivatedError):
        user_activated_validator_service.validate(user=user_to_entity(user))


@pytest.mark.django_db
def test_activation_required(
    settings: SettingsWrapper,
    user_service: BaseUserService,
):
    """Test 'that is_activation_required' returns True if
    AUTH_SEND_ACTIVATION_EMAIL is True."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = True
    assert user_service.is_activation_required()


@pytest.mark.django_db
def test_activation_not_required(
    settings: SettingsWrapper,
    user_service: BaseUserService,
):
    """Test 'that is_activation_required' returns False if
    AUTH_SEND_ACTIVATION_EMAIL is False."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = False
    assert not user_service.is_activation_required()
