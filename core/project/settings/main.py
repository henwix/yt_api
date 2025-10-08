import os
from datetime import timedelta
from pathlib import Path

from django.db import models

from kombu import Queue


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

VERSION = '1.3.7'

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.CustomUser'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # API apps
    'core.apps.channels.apps.ChannelsConfig',
    'core.apps.common.apps.CommonConfig',
    'core.apps.posts.apps.PostsConfig',
    'core.apps.users.apps.UsersConfig',
    'core.apps.videos.apps.VideosConfig',
    'core.apps.reports.apps.ReportsConfig',
    # other
    'rest_framework',
    'django_extensions',
    'django_filters',
    'drf_spectacular',
    'django.contrib.postgres',
    'django_celery_beat',
    'django_celery_results',
    'corsheaders',
    'django_prometheus',
    'social_django',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'core.project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': '5432',
        'DISABLE_SERVER_SIDE_CURSORS': True,
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'core.apps.users.oauth2_backends.CustomGitHubOAuth2',
    'core.apps.users.oauth2_backends.CustomGoogleOAuth2',
    'core.apps.users.oauth2_backends.CustomTwitterOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'core.apps.common.auth_backends.EmailAuthBackend',
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'core.apps.common.throttles.AnonBurstRateThrottle',
        'core.apps.common.throttles.AnonSustainedRateThrottle',
        'core.apps.common.throttles.UserBurstRateThrottle',
        'core.apps.common.throttles.UserSustainedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon_burst': '1000/day',
        'anon_sustained': '100/hour',
        'user_burst': '1000/day',
        'user_sustained': '1000/minute',
    },
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'YouTube-Like-API',
    'DESCRIPTION': '-',
    'VERSION': VERSION,
    'SERVE_INCLUDE_SCHEMA': False,
    'DISABLE_ERRORS_AND_WARNINGS': True,
    'SORT_OPERATIONS': False,
    'SCHEMA_PATH_PREFIX': r'/v[1-2]/',
    'SWAGGER_UI_SETTINGS': {'deepLinking': True, 'persistAuthorization': True},
    'AUTHENTICATION_WHITELIST': ['rest_framework_simplejwt.authentication.JWTAuthentication'],
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': '',
    'AUDIENCE': None,
    'ISSUER': None,
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    'TOKEN_VERIFY_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenVerifySerializer',
    'TOKEN_BLACKLIST_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenBlacklistSerializer',
    'SLIDING_TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer',
    'SLIDING_TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer',
}

LOGIN_REDIRECT_URL = 'v1:users:customuser-me'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '[%(levelname)s] [%(asctime)s] [%(module)s] [%(process)d] '
                '[%(thread)d] %(message)s'
            ),
        },
        'logger': {
            'format': (
                '[%(levelname)s] [%(asctime)s] [%(module)s] [%(process)d] '
                '[%(thread)d] %(message)s \nlog_meta:%(log_meta)s'
            ),
        },
    },
    'filters': {
        'log_meta_filter': {
            "()": "core.project.loggers.LogMetaFilter",
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',  # TODO: change to error or info
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'logger_console': {
            'level': 'DEBUG',  # TODO: change to error or info
            'class': 'logging.StreamHandler',
            'formatter': 'logger',
            'filters': ['log_meta_filter'],
        },
    },
    'loggers': {
        'django.request': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.logger': {
            'level': 'INFO',
            'handlers': ['logger_console'],
            'propagate': False,
        },
    },
}

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'


# Files Storages


STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
    },
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    'local': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
}


# AWS S3 & Cloudfront

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False

AWS_S3_VIDEO_BUCKET_PREFIX = os.environ.get('AWS_S3_VIDEO_BUCKET_PREFIX')
AWS_S3_AVATAR_BUCKET_PREFIX = os.environ.get('AWS_S3_AVATAR_BUCKET_PREFIX')

AWS_CLOUDFRONT_DOMAIN = os.environ.get("AWS_CLOUDFRONT_DOMAIN")
AWS_CLOUDFRONT_KEY_ID = os.environ.get("AWS_CLOUDFRONT_KEY_ID")
AWS_CLOUDFRONT_KEY = (
    os.environ.get("AWS_CLOUDFRONT_KEY").replace("\\n", "\n").encode("ascii").strip()
)


# Celery

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'  # 'django-db'
CELERY_RESULT_EXPIRES = 1  # 1 hour in seconds
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True


CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TASK_QUEUES = (
    Queue('media-queue'),
    Queue('email-queue'),
)


# Email SMTP

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.eu.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

AUTH_SEND_ACTIVATION_EMAIL = False

EMAIL_FRONTEND_PROTOCOL = os.environ.get('EMAIL_FRONTEND_PROTOCOL', 'https')
EMAIL_FRONTEND_DOMAIN = os.environ.get('EMAIL_FRONTEND_DOMAIN', 'example.com')
EMAIL_FRONTEND_PASSWORD_RESET_URI = os.environ.get('EMAIL_FRONTEND_PASSWORD_RESET_URI')
EMAIL_FRONTEND_USERNAME_RESET_URI = os.environ.get('EMAIL_FRONTEND_USERNAME_RESET_URI')
EMAIL_FRONTEND_ACTIVATE_URI = os.environ.get('EMAIL_FRONTEND_ACTIVATE_URI')

EMAIL_SMTP_TEMPLATES = {
    'otp_email': 'users/otp_email.html',
    'set_email': 'users/set_email.html',
    'password_reset': 'users/password_reset_email.html',
    'username_reset': 'users/username_reset_email.html',
    'activate_user': 'users/activate_user_email.html',
}


# Cache keys

CACHE_KEYS = {
    's3_video_url': 's3_video_url_',
    's3_avatar_url': 's3_avatar_url_',
    'related_posts': 'channel_posts_',
    'subs_list': 'subs_',
    'retrieve_channel': 'retrieve_channel_',
    'otp_email': 'otp_code_',
    'set_email': 'set_email_code_',
    'password_reset': 'user_password_reset_',
    'activate_user': 'activate_user_',
}


# OAuth2-social

OAUTH2_ALLOWED_PROVIDERS = {
    'github': 'github',
    'google': 'google-oauth2',
    'x': 'twitter-oauth2',
}

SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_SLUGIFY_USERNAMES = True

SOCIAL_AUTH_GITHUB_KEY = os.environ.get('SOCIAL_AUTH_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('SOCIAL_AUTH_GITHUB_SECRET')
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_TWITTER_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_OAUTH2_KEY')
SOCIAL_AUTH_TWITTER_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_OAUTH2_SECRET')

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',  # connect service to an existing account with the same email
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_DISCONNECT_PIPELINE = (
    'social_core.pipeline.disconnect.allowed_to_disconnect',
    'social_core.pipeline.disconnect.get_entries',
    'social_core.pipeline.disconnect.revoke_tokens',
    'social_core.pipeline.disconnect.disconnect',
)


# Captcha

V3_MIN_GOOGLE_RECAPTCHA_SCORE = 0.5


class CAPTCHA_VERSIONS(models.TextChoices):
    GOOGLE_V3 = 'v3'
    GOOGLE_V2_VISIBLE = 'v2_visible'
    GOOGLE_V2_INVISIBLE = 'v2_invisible'


CAPTCHA_SECRET_KEYS = {
    CAPTCHA_VERSIONS.GOOGLE_V3.value: os.environ.get('V3_GOOGLE_RECAPTCHA_PRIVATE_KEY'),
    CAPTCHA_VERSIONS.GOOGLE_V2_VISIBLE.value: os.environ.get('V2_VISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY'),
    CAPTCHA_VERSIONS.GOOGLE_V2_INVISIBLE.value: os.environ.get('V2_INVISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY'),
}


CAPTCHA_VERSION_SERVICES = {
    CAPTCHA_VERSIONS.GOOGLE_V3.value: 'GoogleV3CaptchaService',
    CAPTCHA_VERSIONS.GOOGLE_V2_VISIBLE.value: 'GoogleV2CaptchaService',
    CAPTCHA_VERSIONS.GOOGLE_V2_INVISIBLE.value: 'GoogleV2CaptchaService',
}
