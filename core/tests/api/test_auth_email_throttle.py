import time

import pytest
from pytest_django.fixtures import SettingsWrapper
from rest_framework.test import APIClient

from core.apps.users.models import CustomUser
from core.tests.factories.channels import UserModelFactory


@pytest.mark.django_db
def test_create_user_throttled_with_enabled_activation(settings: SettingsWrapper, client: APIClient):
    """Test that 429 code has been returned if the throttle_limit has been
    reached and activation email is enabled.

    Throttle with this endpoint doesn't work if the activation email is
    disabled

    """

    settings.AUTH_SEND_ACTIVATION_EMAIL = True
    settings.CAPTCHA_VALIDATION_ENABLED = False

    throttle_limit = 5

    for i in range(1, throttle_limit + 2):  # generate range from 1 to throttle_limit increased by 2
        data = {
            'email': f'{i}_test_email@example.com',
            'username': f'{i}_test_username',
            'password': 'test_password_123',
        }
        response = client.post('/v1/auth/users/', data)

        if i <= throttle_limit:
            assert response.status_code == 201
        else:
            assert response.status_code == 429


@pytest.mark.django_db
def test_create_user_throttled_with_disabled_activation(settings: SettingsWrapper, client: APIClient):
    """Test that 429 code was not returned if the throttle_limit has been
    reached and activation email is disabled.

    Throttle with this endpoint doesn't work if the activation email is
    disabled

    """

    settings.AUTH_SEND_ACTIVATION_EMAIL = False
    settings.CAPTCHA_VALIDATION_ENABLED = False

    throttle_limit = 5

    for i in range(throttle_limit + 1):
        data = {
            'email': f'{i}_test_email@example.com',
            'username': f'{i}_test_username',
            'password': 'test_password_123',
        }
        response = client.post('/v1/auth/users/', data)

        assert response.status_code == 201


@pytest.mark.django_db
def test_create_user_throttled_with_enabled_activation_after_timeout(settings: SettingsWrapper, client: APIClient):
    """Test that 429 code was not returned if the throttle_limit has been
    reached and activation email is disabled.

    Throttle with this endpoint doesn't work if the activation email is
    disabled

    """

    settings.AUTH_SEND_ACTIVATION_EMAIL = True
    settings.CAPTCHA_VALIDATION_ENABLED = False

    throttle_limit = 5
    throttle_timeout = 60  # throttle timeout in seconds. Example: if equals 60 - throttle_limit/minute

    for i in range(1, throttle_limit + 2):  # generate range from 1 to throttle_limit increased by 2
        data = {
            'email': f'{i}_test_email@example.com',
            'username': f'{i}_test_username',
            'password': 'test_password_123',
        }
        response = client.post('/v1/auth/users/', data)

        if i <= throttle_limit:
            assert response.status_code == 201
        else:
            assert response.status_code == 429

    time.sleep(throttle_timeout + 1)
    print(f'timeout: {throttle_timeout}')

    #  send request after throttle timeout
    data = {
        'email': 'timeout_test_email@example.com',
        'username': 'timeout_test_username',
        'password': 'test_password_123',
    }
    response = client.post('/v1/auth/users/', data)

    assert response.status_code == 201


@pytest.mark.django_db
def test_set_email_throttled(client: APIClient, jwt: str):
    """
    set_email: Test that 429 code has been returned if the throttle_limit has been reached
    """

    throttle_limit = 5
    client.credentials(HTTP_AUTHORIZATION=jwt)
    data = {'email': 'test_email@example.com'}

    for _ in range(throttle_limit):
        response = client.post('/v1/auth/users/set_email/', data)
        assert response.status_code == 200

    response = client.post('/v1/auth/users/set_email/', data)
    assert response.status_code == 429


@pytest.mark.django_db
def test_reset_password_throttled(client: APIClient, user: CustomUser):
    """
    reset_password: Test that 429 code has been returned if the throttle_limit has been reached
    """

    throttle_limit = 5
    data = {'email': user.email}

    for _ in range(throttle_limit):
        response = client.post('/v1/auth/users/reset_password/', data)
        assert response.status_code == 200

    response = client.post('/v1/auth/users/reset_password/', data)
    assert response.status_code == 429


@pytest.mark.django_db
def test_reset_username_throttled(client: APIClient, user: CustomUser):
    """
    reset_username: Test that 429 code has been returned if the throttle_limit has been reached
    """

    throttle_limit = 5
    data = {'email': user.email}

    for _ in range(throttle_limit):
        response = client.post('/v1/auth/users/reset_username/', data)
        assert response.status_code == 200

    response = client.post('/v1/auth/users/reset_username/', data)
    assert response.status_code == 429


@pytest.mark.django_db
def test_resend_activation_throttled(settings: SettingsWrapper, client: APIClient):
    """
    resend_activation: Test that 429 code has been returned if the throttle_limit has been reached
    """

    settings.AUTH_SEND_ACTIVATION_EMAIL = True
    user = UserModelFactory.create(is_active=False)

    throttle_limit = 5
    data = {'email': user.email}

    for _ in range(throttle_limit):
        response = client.post('/v1/auth/users/resend_activation/', data)
        assert response.status_code == 200

    response = client.post('/v1/auth/users/resend_activation/', data)
    assert response.status_code == 429
