from urllib.parse import urlencode

import pytest
from pytest_django.fixtures import SettingsWrapper

from core.apps.common.utils import build_frontend_url


@pytest.mark.django_db
def test_url_created_without_uri_and_query_params(
    settings: SettingsWrapper,
):
    settings.FRONTEND_PROTOCOL = 'https'
    settings.FRONTEND_DOMAIN = 'example.com'

    expected_url = f'{settings.FRONTEND_PROTOCOL}://{settings.FRONTEND_DOMAIN}'

    assert build_frontend_url() == expected_url


@pytest.mark.django_db
@pytest.mark.parametrize('expected_uri', ['/auth/activate/', '/auth/reset_password_confirm/', '/auth2/test/'])
def test_url_created_without_query_params(
    expected_uri: str,
    settings: SettingsWrapper,
):
    settings.FRONTEND_PROTOCOL = 'https'
    settings.FRONTEND_DOMAIN = 'example.com'

    expected_url = f'{settings.FRONTEND_PROTOCOL}://{settings.FRONTEND_DOMAIN}{expected_uri}'

    assert build_frontend_url(uri=expected_uri) == expected_url


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
def test_url_created_with_query_params(
    expected_uri: str,
    expected_params: dict,
    settings: SettingsWrapper,
):
    settings.FRONTEND_PROTOCOL = 'https'
    settings.FRONTEND_DOMAIN = 'example.com'

    expected_url = f'{settings.FRONTEND_PROTOCOL}://{settings.FRONTEND_DOMAIN}{expected_uri}'
    result = build_frontend_url(uri=expected_uri, query_params=expected_params)

    assert result == expected_url + '?' + urlencode(expected_params)
