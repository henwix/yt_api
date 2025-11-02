from dataclasses import dataclass

from core.apps.payments.services.stripe_service import BaseStripeService, BaseStripeSubDoesNotExistValidatorService
from core.apps.users.entities import UserEntity


@dataclass
class GetStripeSubStateUseCase:
    stripe_service: BaseStripeService
    stripe_sub_validator_service: BaseStripeSubDoesNotExistValidatorService

    def execute(self, user: UserEntity) -> dict:
        customer_id = self.stripe_service.get_customer_id(user_id=user.id)
        sub_data = self.stripe_service.get_sub_state_by_customer_id(customer_id=customer_id)
        self.stripe_sub_validator_service.validate(sub=sub_data)

        customer_portal_url = self.stripe_service.get_customer_portal_session_url(customer_id=customer_id)

        return {'sub_state': sub_data, 'customer_portal_url': customer_portal_url}
