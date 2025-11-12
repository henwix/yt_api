from dataclasses import dataclass
from logging import Logger

import orjson

from core.apps.payments.enums import StripeSubscriptionStatusesEnum
from core.apps.payments.services.stripe_service import (
    BaseCustomerIdValidatorService,
    BaseStripeEventValidatorService,
    BaseStripeService,
)


@dataclass
class StripeWebhookUseCase:
    stripe_service: BaseStripeService
    event_validator_service: BaseStripeEventValidatorService
    customer_id_validator_service: BaseCustomerIdValidatorService
    logger: Logger

    def execute(self, payload: bytes, signature: str) -> None:
        event = self.stripe_service.construct_event(payload=payload, signature=signature)
        self.event_validator_service.validate(event=event)

        customer_id = event['data']['object'].get('customer')
        self.customer_id_validator_service.validate(customer_id=customer_id)

        subscriptions = self.stripe_service.get_subs_list_by_customer_id(customer_id=customer_id)

        if len(subscriptions) == 0:
            # Customer has no active subscription - could be cancelled or never subscribed
            self.stripe_service.save_sub_state_by_customer_id(
                customer_id=customer_id,
                data={'status': StripeSubscriptionStatusesEnum.CANCELED, 'customer_id': customer_id},
            )
        else:
            self.stripe_service.update_customer_sub_state(customer_id=customer_id, sub=subscriptions.data[0])

        self.logger.info(
            'Stripe Event has been handled',
            extra={'log_meta': orjson.dumps({'stripe_event': event['type']}).decode()},
        )
