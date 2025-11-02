from django.urls import path

from core.api.v1.payments.views import (
    CreateCheckoutSessionView,
    GetStripeSubStateView,
    stripe_webhook_view,
)

app_name = 'payments'


urlpatterns = [
    path('payments/stripe/session/', CreateCheckoutSessionView.as_view(), name='checkout-session-create'),
    path('payments/stripe/webhook/', stripe_webhook_view, name='stripe-webhook'),
    path('payments/subscription_state/', GetStripeSubStateView.as_view(), name='stripe-sub-state'),
]
