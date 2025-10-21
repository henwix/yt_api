from django.db.models import TextChoices


class StripeSubscriptionTiersEnum(TextChoices):
    PRO = 'pro', 'Pro'
    PREMIUM = 'premium', 'Premium'
