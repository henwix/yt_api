from dataclasses import dataclass
from logging import Logger

import orjson

from core.apps.payments.services.stripe_service import BaseStripeService


@dataclass
class UserInvalidateStripeCacheUseCase:
    stripe_service: BaseStripeService
    logger: Logger

    def execute(self, user_id: int) -> None:
        customer_id = self.stripe_service.get_customer_id(user_id=user_id)

        if customer_id is None:
            self.logger.info(
                'Stripe cache not found for user', extra={'log_meta': orjson.dumps({'user_id': user_id}).decode()}
            )
            return

        self.stripe_service.delete_sub_state_by_customer_id(customer_id=customer_id)
        self.stripe_service.delete_customer_id(user_id=user_id)

        self.logger.info(
            'Stripe cache invalidated for user',
            extra={'log_meta': orjson.dumps({'user_id': user_id, 'customer_id': customer_id}).decode()},
        )
