from django.db.utils import settings

STRIPE_ALLOWED_EVENTS = [
    'checkout.session.completed',
    'customer.subscription.created',
    'customer.subscription.updated',
    'customer.subscription.deleted',
    'customer.subscription.trial_will_end',
    'invoice.paid',
    'invoice.payment_failed',
    'payment_intent.payment_failed',
    'payment_intent.canceled',
]

STRIPE_SUBSCRIPTION_TIERS = {
    'pro': settings.STRIPE_SUB_PRICE_PRO,
    'premium': settings.STRIPE_SUB_PRICE_PREMIUM,
}
