from django.db.utils import settings

from core.apps.common.enums import CaptchaVersionsEnum

# Captcha
CAPTCHA_SECRET_KEYS = {
    CaptchaVersionsEnum.GOOGLE_V3.value: settings.V3_GOOGLE_RECAPTCHA_PRIVATE_KEY,
    CaptchaVersionsEnum.GOOGLE_V2_VISIBLE.value: settings.V2_VISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY,
    CaptchaVersionsEnum.GOOGLE_V2_INVISIBLE.value: settings.V2_INVISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY,
}


CAPTCHA_VERSION_SERVICES = {
    CaptchaVersionsEnum.GOOGLE_V3.value: 'GoogleV3CaptchaService',
    CaptchaVersionsEnum.GOOGLE_V2_VISIBLE.value: 'GoogleV2CaptchaService',
    CaptchaVersionsEnum.GOOGLE_V2_INVISIBLE.value: 'GoogleV2CaptchaService',
}

V3_MIN_GOOGLE_RECAPTCHA_SCORE = 0.5


# Cache keys

CACHE_KEYS = {
    's3_video_url': 's3:video_url:',
    's3_avatar_url': 's3:avatar_url:',
    'related_posts': 'channel:posts:',
    'subs_list': 'channel:subs:',
    'retrieve_channel': 'channel:retrieve:',
    'otp_email': 'email:otp_code:',
    'set_email': 'email:set_email_code:',
    'password_reset': 'email:user_password_reset:',
    'activate_user': 'email:activate_user:',
    'stripe_customer_id': 'stripe:user:',
    'stripe_sub_data': 'stripe:customer:',
    'stripe_customer_portal': 'stripe:customer_portal:',
}


# Email SMTP templates

EMAIL_SMTP_TEMPLATES = {
    'otp_email': 'users/otp_email.html',
    'set_email': 'users/set_email.html',
    'password_reset': 'users/password_reset_email.html',
    'username_reset': 'users/username_reset_email.html',
    'activate_user': 'users/activate_user_email.html',
}
