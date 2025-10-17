from dataclasses import dataclass

import stripe

from core.apps.payments.services.stripe_service import BaseStripeService
from core.apps.users.entities import UserEntity


@dataclass
class CreateCheckoutSessionUseCase:
    stripe_service: BaseStripeService

    def execute(self, sub_tier: str, user: UserEntity) -> str:
        stripe_customer_id = self.stripe_service.get_customer_id(user_id=user.id)

        if not stripe_customer_id:
            new_customer = self.stripe_service.create_customer(email=user.email, user_id=user.id)
            self.stripe_service.save_customer_id(user_id=user.id, customer_id=new_customer.id)
            stripe_customer_id = new_customer.id

        session = stripe.checkout.Session.create(
            api_key=self.stripe_service.get_api_key(),
            mode='subscription',
            customer='cus_test',
            line_items=[{'price': 'price_test', 'quantity': 1}],
            success_url='http://localhost:80/success/',
            cancel_url='http://localhost:80/cancel/',
            metadata={'test': 'asd'},
            allow_promotion_codes=True,
        )

        return session.url
