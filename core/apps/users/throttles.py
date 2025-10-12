from rest_framework.throttling import UserRateThrottle


class OAuth2Throttle(UserRateThrottle):
    scope = 'oauth2_token'
    rate = '5/minute'


class UserAuthEmailSendThrottle(UserRateThrottle):
    scope = 'auth_email_send'
    rate = '5/minute'

    def get_cache_key(self, request, view):
        return super().get_cache_key(request, view) + f'_{view.action}'


class UserAuthLoginThrottle(UserRateThrottle):
    scope = 'auth_login'
    rate = '5/minute'
