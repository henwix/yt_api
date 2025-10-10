import os

from .main import *  # noqa


DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('PGBOUNCER_HOST'),  # pgbouncer host
        'PORT': '5432',  # pgbouncer port
        'CONN_MAX_AGE': 0,
    },
}

CSRF_TRUSTED_ORIGINS = [
    f"https://{os.environ.get('ADMIN_DOMAIN')}",
    f"https://{os.environ.get('ADMIN_DOMAIN')}:443",
]

ALLOWED_HOSTS = [
    os.environ.get('API_DOMAIN'),
]

CORS_ALLOWED_ORIGINS = [
    f"https://{os.environ.get('API_DOMAIN')}",
    f"https://{os.environ.get('API_DOMAIN')}:443",
    f"https://{os.environ.get('ADMIN_DOMAIN')}",
    f"https://{os.environ.get('ADMIN_DOMAIN')}:443",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGGING['handlers']['console']['level'] = 'INFO'  # noqa
LOGGING['handlers']['logger_console']['level'] = 'INFO'  # noqa

if not DEBUG:
    STATIC_ROOT = BASE_DIR / 'static'  # noqa
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 60  # 31536000 - 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
