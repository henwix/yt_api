from .main import *  # noqa


DEBUG = True

INSTALLED_APPS.append('silk')  # noqa

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]
