import pytest

from core.apps.users.services.users import BaseUserService
from core.tests.factories.channels import UserModelFactory


@pytest.mark.skip('not finished')
def test_user_authentication_by_username(user_service: BaseUserService):
    password = '1234q1234q'
    user = UserModelFactory.create(password=password)

    received_user = user_service.authenticate(
        login=user.username,
        password=password,
    )

    assert user == received_user
