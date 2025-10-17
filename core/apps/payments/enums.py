from django.db.models import TextChoices


class StripeSubscriptionTiersEnum(TextChoices):
    PLUS = 'plus', 'Plus'
    PREMIUM = 'premium', 'Premium'
