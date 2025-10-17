from abc import (
    ABC,
    abstractmethod,
)

from django.db.utils import settings

import stripe


class BaseStripeProvider(ABC):
    @abstractmethod
    def create_customer(self, email: str, user_id: int) -> stripe.Customer:
        ...


class StripeProvider(BaseStripeProvider):
    def create_customer(self, email: str, user_id: int) -> stripe.Customer:
        customer: stripe.Customer = stripe.Customer.create(
            api_key=settings.STRIPE_SECRET_KEY,
            email=email,
            metadata={
                'user_id': user_id,
            },
        )
        return customer
