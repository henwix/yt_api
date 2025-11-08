from rest_framework import serializers

from core.apps.payments.enums import StripeSubscriptionPaidTiersEnum, StripeSubscriptionStatusesEnum


class StripeSubscriptionInSerializer(serializers.Serializer):
    sub_tier = serializers.ChoiceField(
        choices=StripeSubscriptionPaidTiersEnum.choices,
        help_text='Subscription tier',
    )


class StripeCustomerPortalUrlSerializer(serializers.Serializer):
    customer_portal_url = serializers.URLField(help_text='Stripe customer portal URL')


class StripeSubscriptionSerializer(serializers.Serializer):
    subscription_id = serializers.CharField(
        min_length=28,
        max_length=28,
        help_text='Unique identifier for the subscription',
    )
    customer_id = serializers.CharField(
        min_length=18,
        max_length=18,
        help_text='Unique identifier for the customer',
    )
    status = serializers.ChoiceField(
        choices=StripeSubscriptionStatusesEnum.choices,
        help_text='Subscription status',
    )
    price_id = serializers.CharField(
        min_length=30,
        max_length=30,
        help_text='Unique identifier for the subscription price',
    )
    tier = serializers.ChoiceField(
        choices=StripeSubscriptionPaidTiersEnum.choices,
        help_text='Subscription tier',
    )
    current_period_start = serializers.IntegerField(
        help_text="The start time of this subscription item's current billing period",
    )
    current_period_end = serializers.IntegerField(
        help_text="The end time of this subscription item's current billing period",
    )
    cancel_at_period_end = serializers.BooleanField(
        help_text='Whether this subscription will cancel at the end of the current billing period',
    )
    payment_method = serializers.DictField(
        allow_null=True,
        child=serializers.CharField(),
        help_text='Current payment method',
    )


class StripeSubscriptionStateOutSerializer(StripeCustomerPortalUrlSerializer):
    sub_state = StripeSubscriptionSerializer()
