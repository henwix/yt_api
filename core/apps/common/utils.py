from urllib.parse import urlencode

from django.db.utils import settings


def build_frontend_url(uri: str | None = None, query_params: dict | None = None) -> str:
    base_url = f'{settings.FRONTEND_PROTOCOL}://{settings.FRONTEND_DOMAIN}'

    if uri:
        base_url += uri if uri.startswith('/') else f'/{uri}'
    if query_params:
        base_url += f'?{urlencode(query_params)}'

    return base_url
