from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

import punq
import pytest

from core.apps.users.converters.users import user_from_entity
from core.apps.users.exceptions.users import UserNotFoundError
from core.apps.users.services.users import (
    BaseUserService,
    BaseUserValidatorService,
)
from core.project.containers import get_container
from core.tests.factories.channels import UserModelFactory


User = get_user_model()


@pytest.mark.django_db
def test_user_authentication(user_service: BaseUserService):
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
    container: punq.Container = get_container()
    validator_service: BaseUserValidatorService = container.resolve(BaseUserValidatorService)

    with pytest.raises(UserNotFoundError):
        validator_service.validate(user=None)


@pytest.mark.django_db
def test_get_user_by_email(user_service: BaseUserService, user: User):
    user_dto = user_from_entity(user_service.get_by_email(user.email))

    assert user == user_dto


@pytest.mark.django_db
def test_jwt_generated_for_user(user_service: BaseUserService, client: APIClient, user: User):
    tokens = user_service.generate_jwt(user=user)
    client.credentials(HTTP_AUTHORIZATION=tokens.get('access'))

    access_response = client.post('/api/v1/token/verify/', {'token': tokens.get('access')})
    refresh_response = client.post('/api/v1/token/verify/', {'token': tokens.get('refresh')})

    assert access_response.status_code == 200
    assert refresh_response.status_code == 200
