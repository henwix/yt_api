from .main import *  # noqa


DEBUG = False

CSRF_TRUSTED_ORIGINS = ['http://localhost:8001', 'http://127.0.0.1:8001']

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DJOSER = {
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': False,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm?uid={uid}&token={token}',
    'USERNAME_RESET_CONFIRM_URL': 'username/reset/confirm?uid={uid}&token={token}',
    'ACTIVATION_URL': 'activate/?uid={uid}&token={token}',
    'EMAIL_FRONTEND_DOMAIN': 'front-domain.com',
    'EMAIL_FRONTEND_SITE_NAME': 'YT',
    'SERIALIZERS': {
        'user_create': 'core.apps.users.serializers.CustomUserCreateSerializer',
        'user_create_password_retype': 'core.apps.users.serializers.CustomUserCreatePasswordRetypeSerializer',
        'user': 'core.apps.users.serializers.CustomUserSerializer',
        'current_user': 'core.apps.users.serializers.CustomUserSerializer',
    },
}
