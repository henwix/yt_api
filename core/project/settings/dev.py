from .main import *  # noqa


DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]

#  set throttles for testing
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {  # noqa
    'anon_burst': '1000000/day',
    'anon_sustained': '10000000/hour',
    'user_burst': '100000000/day',
    'user_sustained': '10000000/minute',
}

#  add middlewares and installed_apps for dev mode
INSTALLED_APPS.append('silk')  # noqa
MIDDLEWARE.append('silk.middleware.SilkyMiddleware')  # noqa
