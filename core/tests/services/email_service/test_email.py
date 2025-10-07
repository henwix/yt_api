from urllib.parse import urlencode

import pytest
from pytest_django.fixtures import SettingsWrapper

from core.apps.common.services.smtp_email import BaseEmailService


@pytest.mark.django_db
@pytest.mark.parametrize('expected_uri', ['/auth/activate/', '/auth/reset_password_confirm/', '/auth2/test/'])
def test_email_url_created_without_query_params(
    expected_uri: str,
    settings: SettingsWrapper,
    email_service: BaseEmailService,
):
    settings.EMAIL_FRONTEND_PROTOCOL = 'https'
    settings.EMAIL_FRONTEND_DOMAIN = 'example.com'

    expected_url = f'{settings.EMAIL_FRONTEND_PROTOCOL}://{settings.EMAIL_FRONTEND_DOMAIN}{expected_uri}'

    assert email_service.build_email_frontend_url(uri=expected_uri) == expected_url


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_uri, expected_params',
    argvalues=[
        ('/auth/activate/', {'uid': 'MZY3', 'code': 'askljfhaslkfj1gh2i'}),
        ('/auth/reset_password_confirm/', {'uid': 'CA1r', 'code': 'as2189437291y4hasf'}),
        ('/test/test/', {'test': 'Test', 'test_2': 'test_2'}),
        ('/hello/world/', {'hello': 'world'}),
    ],
)
def test_email_url_created_with_query_params(
    expected_uri: str,
    expected_params: dict,
    settings: SettingsWrapper,
    email_service: BaseEmailService,
):
    settings.EMAIL_FRONTEND_PROTOCOL = 'https'
    settings.EMAIL_FRONTEND_DOMAIN = 'example.com'

    expected_url = f'{settings.EMAIL_FRONTEND_PROTOCOL}://{settings.EMAIL_FRONTEND_DOMAIN}{expected_uri}'
    result = email_service.build_email_frontend_url(expected_uri, expected_params)

    assert result == expected_url + '?' + urlencode(expected_params)
