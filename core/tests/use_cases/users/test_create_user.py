from django.utils.text import slugify

import pytest
from pytest_django.fixtures import SettingsWrapper

from core.apps.channels.models import Channel
from core.apps.users.models import CustomUser
from core.apps.users.use_cases.users.user_create import UserCreateUseCase


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_username, expected_email, expected_password',
    argvalues=(
        ['test_username12345', 'MyTestUsername994', 'asljdhalskfjg'],
        ['test_email_1234@test.com', 'mytest_email@example.com', 'jsdfijsdfks@gmail.com'],
        ['Test_Password_123', 'LKjha3s248', 'Akajsf1518gsAF'],
    ),
)
def test_user_created_with_no_activation(
    settings: SettingsWrapper,
    user_create_use_case: UserCreateUseCase,
    expected_username: str,
    expected_email: str,
    expected_password: str,
):
    """Test that the user has been created without activation email."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = False
    expected_is_active = True

    result: CustomUser = user_create_use_case.execute(
        validated_data={
            'username': expected_username,
            'email': expected_email,
            'password': expected_password,
        },
    )

    assert isinstance(result, CustomUser)
    assert result.is_active == expected_is_active
    assert result.username == expected_username
    assert result.email == expected_email
    assert result.check_password(expected_password)


@pytest.mark.django_db
def test_user_created_with_activation(
    settings: SettingsWrapper,
    user_create_use_case: UserCreateUseCase,
):
    """Test that the user has been created with activation email."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = True
    expected_username = 'test_username'
    expected_email = 'test_email@test.com'
    expected_password = 'password_123456_ABC'
    expected_is_active = False

    result: dict = user_create_use_case.execute(
        validated_data={
            'username': expected_username,
            'email': expected_email,
            'password': expected_password,
        },
    )

    created_user = CustomUser.objects.get(username=expected_username)

    assert isinstance(result, dict)
    assert created_user.is_active == expected_is_active
    assert created_user.username == expected_username
    assert created_user.email == expected_email
    assert created_user.check_password(expected_password)


@pytest.mark.django_db
def test_channel_created_based_on_user_data(
    settings: SettingsWrapper,
    user_create_use_case: UserCreateUseCase,
):
    """Test that channel has been created based on provided user's data."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = False
    expected_username = 'username_test'
    expected_email = 'email@test.com'
    expected_password = 'Test_PasswordAMsnfla'

    user_create_use_case.execute(
        validated_data={
            'username': expected_username,
            'email': expected_email,
            'password': expected_password,
        },
    )

    assert Channel.objects.filter(
        user__username=expected_username,
        user__email=expected_email,
        slug=expected_username,
        name=expected_username,
        country=None,
        description=None,
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_channel_name, expected_channel_slug, expected_channel_description, expected_channel_country',
    argvalues=(
        ['Test Channel Name', 'test_channel_slug', 'Test Channel description', 'US'],
        ['Channel.name1235', 'mytest_channel_slug-123', 'Testchanneldescription', 'United States'],
        ['channeln@mete$t', 'channel_slug-123', 'description', 'Test Country'],
        ['this is a test channel name', 'gfldsfsad-akslnf1_sad', 'FN(*LASJKFHn;ajkfho1b', 'Channel Country Test'],
    ),
)
def test_channel_created_with_provided_data(
    settings: SettingsWrapper,
    user_create_use_case: UserCreateUseCase,
    expected_channel_name: str,
    expected_channel_slug: str,
    expected_channel_description: str,
    expected_channel_country: str,
):
    """Test that channel has been created based on provided channel data."""

    settings.AUTH_SEND_ACTIVATION_EMAIL = False
    expected_username = 'username_test'
    expected_email = 'test_email@test.com'
    expected_password = 'PasswordTest_123456'

    user_create_use_case.execute(
        validated_data={
            'username': expected_username,
            'email': expected_email,
            'password': expected_password,
            'channel': {
                'name': expected_channel_name,
                'slug': expected_channel_slug,
                'description': expected_channel_description,
                'country': expected_channel_country,
            },
        },
    )

    assert Channel.objects.filter(
        user__username=expected_username,
        user__email=expected_email,
        slug=expected_channel_slug,
        name=expected_channel_name,
        country=expected_channel_country,
        description=expected_channel_description,
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('expected_channel_name', ['ChannelTestName', 'Channel test name', 'name1235_152. test name'])
def test_channel_created_without_slug_data(
    settings: SettingsWrapper,
    user_create_use_case: UserCreateUseCase,
    expected_channel_name: str,
):
    """Test that channel has been created without provided channel slug.

    Slug must be generated based on channel's name

    """

    settings.AUTH_SEND_ACTIVATION_EMAIL = False
    expected_username = 'username_test'
    expected_email = 'test_email@test.com'
    expected_password = 'PasswordTest_123456'
    expected_channel_description = 'My test channel description'
    expected_channel_country = 'My test channel country'

    user_create_use_case.execute(
        validated_data={
            'username': expected_username,
            'email': expected_email,
            'password': expected_password,
            'channel': {
                'name': expected_channel_name,
                'description': expected_channel_description,
                'country': expected_channel_country,
            },
        },
    )

    assert Channel.objects.filter(
        user__username=expected_username,
        user__email=expected_email,
        slug=slugify(expected_channel_name),
        name=expected_channel_name,
        country=expected_channel_country,
        description=expected_channel_description,
    ).exists()
