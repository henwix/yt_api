from core.apps.payments.enums import StripeSubscriptionAllTiersEnum

POSTS_LIMITS_BY_SUBSCRIPTION_TIER = {
    StripeSubscriptionAllTiersEnum.FREE: 7,
    StripeSubscriptionAllTiersEnum.PREMIUM: 10,
    StripeSubscriptionAllTiersEnum.PRO: 15,
}
