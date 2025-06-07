from .main import *  # noqa


DEBUG = True

CSRF_TRUSTED_ORIGINS = [
    'https://localhost',
    'https://localhost:443',
    'https://127.0.0.1',
    'https://127.0.0.1:443',
]

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

CORS_ALLOWED_ORIGINS = [
    'https://localhost',
    'https://localhost:443',
    'https://127.0.0.1',
    'https://127.0.0.1:443',
    'https://127.0.0.1:5500',
    'http://127.0.0.1:5500',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


if not DEBUG:
    STATIC_ROOT = BASE_DIR / 'static'  # noqa
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True

    # SECURE_HSTS_SECONDS = 60  # 31536000 - 1 year
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
