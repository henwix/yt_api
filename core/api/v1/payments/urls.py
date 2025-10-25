from django.urls import path

from core.api.v1.payments.views import (
    CreateCheckoutSessionView,
    stripe_sub_state,
    stripe_webhook_view,
)

app_name = 'payments'


urlpatterns = [
    path('payments/stripe/session/', CreateCheckoutSessionView.as_view(), name='checkout-session-create'),
    path('payments/stripe/webhook/', stripe_webhook_view, name='stripe-webhook'),
    path('payments/subscription_state/', stripe_sub_state, name='stripe-sub-state'),
]
