from core.apps.payments.enums import StripeSubscriptionAllTiersEnum

POSTS_LIMITS_BY_SUBSCRIPTION_TIER = {
    StripeSubscriptionAllTiersEnum.FREE: 15,
    StripeSubscriptionAllTiersEnum.PREMIUM: 30,
    StripeSubscriptionAllTiersEnum.PRO: 100,
}
