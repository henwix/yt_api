from rest_framework.throttling import UserRateThrottle


class CheckoutSessionThrottle(UserRateThrottle):
    scope = 'checkout_session'
    rate = '1/minute'
