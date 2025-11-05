from django.db.models import TextChoices


class StripeSubscriptionPaidTiersEnum(TextChoices):
    PRO = 'pro', 'Pro'
    PREMIUM = 'premium', 'Premium'


class StripeSubscriptionAllTiersEnum(TextChoices):
    FREE = 'free', 'Free'
    PRO = 'pro', 'Pro'
    PREMIUM = 'premium', 'Premium'


class StripeSubscriptionStatusesEnum(TextChoices):
    INCOMPLETE = 'incomplete', 'Incomplete'
    INCOMPLETE_EXPIRED = 'incomplete_expired', 'Incomplete expired'
    TRIALING = 'trialing', 'Trialing'
    ACTIVE = 'active', 'Active'
    PAST_DUE = 'past_due', 'Past due'
    CANCELED = 'canceled', 'Canceled'
    UNPAID = 'unpaid', 'Unpaid'
    PAUSED = 'paused', 'Paused'
