from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable

import stripe
from django.db.utils import settings

from core.apps.payments.exceptions import StripeSignatureVerificationError


class BaseStripeProvider(ABC):
    @abstractmethod
    def create_customer(self, email: str, user_id: int) -> stripe.Customer: ...

    @abstractmethod
    def create_checkout_session(self, customer_id: str, user_id: int, sub_price: str) -> stripe.checkout.Session: ...

    @abstractmethod
    def construct_event(self, payload: bytes, signature: str) -> stripe.Event: ...

    @abstractmethod
    def get_subs_list(
        self,
        status: str,
        customer_id: str | None = None,
        limit: int = 10,
        expand: list | None = None,
    ) -> Iterable[stripe.Subscription]: ...


class StripeProvider(BaseStripeProvider):
    _STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
    _STRIPE_WEBHOOK_KEY = settings.STRIPE_WEBHOOK_KEY

    def create_customer(self, email: str, user_id: int) -> stripe.Customer:
        customer: stripe.Customer = stripe.Customer.create(
            api_key=self._STRIPE_SECRET_KEY,
            email=email,
            metadata={
                'user_id': user_id,
            },
        )
        return customer

    def create_checkout_session(self, customer_id: str, user_id: int, sub_price: str) -> stripe.checkout.Session:
        return stripe.checkout.Session.create(
            api_key=self._STRIPE_SECRET_KEY,
            mode='subscription',
            customer=customer_id,
            line_items=[
                {
                    'price': sub_price,
                    'quantity': 1,
                },
            ],
            success_url='http://localhost:80/success/',
            cancel_url='http://localhost:80/cancel/',
            subscription_data={
                'metadata': {
                    'user_id': user_id,
                },
            },
            allow_promotion_codes=True,
        )

    def construct_event(self, payload: bytes, signature: str) -> stripe.Event:
        try:
            return stripe.Webhook.construct_event(
                payload,
                signature,
                self._STRIPE_WEBHOOK_KEY,
            )
        except (ValueError, stripe.SignatureVerificationError) as error:
            raise StripeSignatureVerificationError(error_msg=str(error))

    def get_subs_list(
        self,
        status: str,
        customer_id: str | None = None,
        limit: int = 10,
        expand: list | None = None,
    ) -> Iterable[stripe.Subscription]:
        subscriptions = stripe.Subscription.list(
            api_key=self._STRIPE_SECRET_KEY,
            customer=customer_id,
            limit=limit,
            status=status,
            expand=expand,
        )
        return subscriptions
