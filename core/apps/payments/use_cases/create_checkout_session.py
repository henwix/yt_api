from dataclasses import dataclass

from core.apps.payments.services.stripe_service import (
    BaseStripeService,
    BaseStripeSubValidatorService,
)
from core.apps.users.entities import UserEntity


@dataclass
class CreateCheckoutSessionUseCase:
    stripe_service: BaseStripeService
    sub_validator_service: BaseStripeSubValidatorService

    def execute(self, sub_tier: str, user: UserEntity) -> str:
        stripe_customer_id = self.stripe_service.get_customer_id(user_id=user.id)

        if stripe_customer_id is None:
            new_customer = self.stripe_service.create_customer(email=user.email, user_id=user.id)
            self.stripe_service.save_customer_id(user_id=user.id, customer_id=new_customer.id)
            stripe_customer_id = new_customer.id
        else:
            existing_sub = self.stripe_service.get_sub_by_customer_id(customer_id=stripe_customer_id)
            self.sub_validator_service.validate(sub=existing_sub)

        session = self.stripe_service.create_checkout_session(
            customer_id=stripe_customer_id,
            user_id=user.id,
            sub_tier=sub_tier,
        )

        return session.url
