from django.db.models import TextChoices


class StripeSubscriptionPaidTiersEnum(TextChoices):
    PRO = 'pro', 'Pro'
    PREMIUM = 'premium', 'Premium'


class StripeSubscriptionAllTiersEnum(TextChoices):
    FREE = 'free', 'Free'
    PRO = 'pro', 'Pro'
    PREMIUM = 'premium', 'Premium'
