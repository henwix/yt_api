from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AnonBurstRateThrottle(AnonRateThrottle):
    scope = 'anon_burst'


class AnonSustainedRateThrottle(AnonRateThrottle):
    scope = 'anon_sustained'


class UserBurstRateThrottle(UserRateThrottle):
    scope = 'user_burst'


class UserSustainedRateThrottle(UserRateThrottle):
    scope = 'user_sustained'
