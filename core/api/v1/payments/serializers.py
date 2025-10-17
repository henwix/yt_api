from rest_framework import serializers

from core.apps.payments.enums import StripeSubscriptionTiersEnum


class StripeSubscriptionSerializer(serializers.Serializer):
    sub_tier = serializers.ChoiceField(
        choices=StripeSubscriptionTiersEnum.choices,
        help_text='Stripe Subscription Tier',
    )
