from rest_framework import serializers

from core.apps.payments.enums import StripeSubscriptionPaidTiersEnum


class StripeSubscriptionInSerializer(serializers.Serializer):
    sub_tier = serializers.ChoiceField(
        choices=StripeSubscriptionPaidTiersEnum.choices,
        help_text='Stripe Subscription Tier',
    )
