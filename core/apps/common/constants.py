from django.db import models
from django.db.utils import settings


# Captcha

class CAPTCHA_VERSIONS(models.TextChoices):
    GOOGLE_V3 = 'v3'
    GOOGLE_V2_VISIBLE = 'v2_visible'
    GOOGLE_V2_INVISIBLE = 'v2_invisible'


CAPTCHA_SECRET_KEYS = {
    CAPTCHA_VERSIONS.GOOGLE_V3.value: settings.V3_GOOGLE_RECAPTCHA_PRIVATE_KEY,
    CAPTCHA_VERSIONS.GOOGLE_V2_VISIBLE.value: settings.V2_VISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY,
    CAPTCHA_VERSIONS.GOOGLE_V2_INVISIBLE.value: settings.V2_INVISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY,
}


CAPTCHA_VERSION_SERVICES = {
    CAPTCHA_VERSIONS.GOOGLE_V3.value: 'GoogleV3CaptchaService',
    CAPTCHA_VERSIONS.GOOGLE_V2_VISIBLE.value: 'GoogleV2CaptchaService',
    CAPTCHA_VERSIONS.GOOGLE_V2_INVISIBLE.value: 'GoogleV2CaptchaService',
}

V3_MIN_GOOGLE_RECAPTCHA_SCORE = 0.5


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
    'stripe_customer_id': 'stripe:user:',
    'stripe_sub_data': 'stripe:customer:',
}


# Email SMTP templates

EMAIL_SMTP_TEMPLATES = {
    'otp_email': 'users/otp_email.html',
    'set_email': 'users/set_email.html',
    'password_reset': 'users/password_reset_email.html',
    'username_reset': 'users/username_reset_email.html',
    'activate_user': 'users/activate_user_email.html',
}
