from rest_framework.throttling import UserRateThrottle


class OAuth2ThrottleClass(UserRateThrottle):
    scope = 'oauth2_convert_token'
    rate = '5/min'
